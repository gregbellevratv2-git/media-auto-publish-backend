from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import io
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from database import get_session
from models import Post, User
from auth import get_current_user
from image_utils import combine_and_resize_images, upload_image_to_cloudinary
from scheduler_service import schedule_new_post, remove_scheduled_post, send_post_now_manual, reschedule_post

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/", response_model=List[Post])
def read_posts(
    skip: int = 0, 
    limit: int = 100, 
    platform: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    query = select(Post).where(Post.user_id == current_user.id)
    if platform:
        query = query.where(Post.platform == platform)
    query = query.order_by(Post.scheduled_at.desc()).offset(skip).limit(limit)
    return session.exec(query).all()

@router.post("/", response_model=Post)
def create_post(
    post: Post, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    post.user_id = current_user.id
    session.add(post)
    session.commit()
    session.refresh(post)
    
    # Schedule the post
    schedule_new_post(post.id, post.scheduled_at)
    
    return post

@router.post("/upload")
async def upload_image(
    files: List[UploadFile] = File(...),
    platform: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    # Read files into memory
    image_data_list = []
    for file in files:
        content = await file.read()
        image_data_list.append(io.BytesIO(content))
        
    # Combine and resize
    # Note: combine_and_resize_images expects paths or file-like objects. 
    # We modified it to handle file-like objects in logic, but let's double check image_utils.py
    # Actually, my previous edit to image_utils.py handled paths. I need to ensure it handles BytesIO.
    # Let's assume for a moment I need to fix image_utils.py to handle BytesIO if it doesn't already.
    # Wait, I see in my previous thought I said "image_paths ici peuvent être des chemins locaux... ou des objets file-like".
    # But the code I wrote: `img = Image.open(path)` works with BytesIO too!
    
    processed_image = combine_and_resize_images(image_data_list, platform)
    
    if not processed_image:
        raise HTTPException(status_code=400, detail="Error processing images")
        
    # Upload to Cloudinary
    image_url = upload_image_to_cloudinary(processed_image)
    
    if not image_url:
        raise HTTPException(status_code=500, detail="Error uploading to Cloudinary")
        
    return {"image_url": image_url}

@router.put("/{post_id}", response_model=Post)
def update_post(
    post_id: int, 
    post_update: Post, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    post = session.get(Post, post_id)
    if not post or post.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Update fields
    post.title = post_update.title
    post.text_content = post_update.text_content
    post.image_url = post_update.image_url
    post.platform = post_update.platform
    
    # Check if schedule changed
    if post.scheduled_at != post_update.scheduled_at:
        post.scheduled_at = post_update.scheduled_at
        reschedule_post(post.id, post.scheduled_at)
        
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@router.delete("/{post_id}")
def delete_post(
    post_id: int, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    post = session.get(Post, post_id)
    if not post or post.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Post not found")
        
    remove_scheduled_post(post.id)
    session.delete(post)
    session.commit()
    return {"ok": True}

@router.post("/{post_id}/send-now")
def send_now(
    post_id: int, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    post = session.get(Post, post_id)
    if not post or post.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Post not found")
        
    success, message = send_post_now_manual(post.id, session)
    if not success:
        raise HTTPException(status_code=500, detail=message)
        
    return {"status": "published", "message": message}

@router.post("/check-pending-posts")
def check_pending_posts(
    session: Session = Depends(get_session)
):
    """
    Vérifie et publie tous les posts programmés dont la date est dépassée.
    Utilisé pour rattraper les publications manquées pendant le sommeil du serveur.
    IMPORTANT: Utilise UTC pour la cohérence avec les datetimes stockés en base.
    """
    now = datetime.utcnow()
    
    # Trouver tous les posts programmés dont la date est passée
    query = select(Post).where(
        Post.status == 'scheduled',
        Post.scheduled_at <= now
    )
    pending_posts = session.exec(query).all()
    
    published_count = 0
    failed_count = 0
    results = []
    
    for post in pending_posts:
        success, message = send_post_now_manual(post.id, session)
        if success:
            published_count += 1
            results.append(f"✓ Post #{post.id} publié")
        else:
            failed_count += 1
            results.append(f"✗ Post #{post.id} échec: {message}")
    
    return {
        "checked_at": now.isoformat(),
        "total_pending": len(pending_posts),
        "published": published_count,
        "failed": failed_count,
        "details": results
    }

