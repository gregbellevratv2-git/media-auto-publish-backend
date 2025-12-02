import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Plus, Calendar, Clock, Send, Trash2, Image as ImageIcon } from 'lucide-react';
import api from '../api';
import CreatePostModal from '../components/CreatePostModal';
import CalendarView from '../components/CalendarView';

export default function Dashboard() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [viewMode, setViewMode] = useState('list'); // 'list' or 'calendar'
    const [editingPost, setEditingPost] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchPosts();
    }, []);

    const fetchPosts = async () => {
        try {
            const response = await api.get('/posts');
            setPosts(response.data);
        } catch (error) {
            console.error('Erreur lors du chargement des posts:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const handleDelete = async (postId) => {
        if (!confirm('Supprimer cette publication ?')) return;

        try {
            await api.delete(`/posts/${postId}`);
            setPosts(posts.filter(p => p.id !== postId));
        } catch (error) {
            alert('Erreur lors de la suppression');
        }
    };

    const handleSendNow = async (postId) => {
        if (!confirm('Envoyer cette publication immédiatement ?')) return;

        try {
            await api.post(`/posts/${postId}/send-now`);
            alert('Publication envoyée !');
            fetchPosts();
        } catch (error) {
            alert('Erreur lors de l\'envoi');
        }
    };

    const getStatusBadge = (status) => {
        const styles = {
            scheduled: 'bg-blue-100 text-blue-800',
            sent: 'bg-green-100 text-green-800',
            failed: 'bg-red-100 text-red-800',
        };

        const labels = {
            scheduled: 'Programmé',
            sent: 'Envoyé',
            failed: 'Échec',
        };

        return (
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
                {labels[status] || status}
            </span>
        );
    };

    const getPlatformIcon = (platform) => {
        const icons = {
            linkedin: '💼',
            instagram: '📷',
            facebook: '👥',
        };
        return icons[platform] || '📱';
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900">📅 Media Auto Publish</h1>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 transition"
                    >
                        <LogOut size={20} />
                        <span>Déconnexion</span>
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">Mes publications</h2>
                    <div className="flex gap-3">
                        <div className="bg-white rounded-lg p-1 flex shadow-sm border">
                            <button
                                onClick={() => setViewMode('list')}
                                className={`p-2 rounded-md transition ${viewMode === 'list' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
                                title="Vue Liste"
                            >
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-medium">Liste</span>
                                </div>
                            </button>
                            <button
                                onClick={() => setViewMode('calendar')}
                                className={`p-2 rounded-md transition ${viewMode === 'calendar' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
                                title="Vue Calendrier"
                            >
                                <div className="flex items-center gap-2">
                                    <Calendar size={20} />
                                    <span className="text-sm font-medium">Calendrier</span>
                                </div>
                            </button>
                        </div>
                        <button
                            onClick={() => setShowModal(true)}
                            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition shadow-sm"
                        >
                            <Plus size={20} />
                            <span>Nouvelle publication</span>
                        </button>
                    </div>
                </div>

                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    </div>
                ) : posts.length === 0 ? (
                    <div className="bg-white rounded-lg shadow p-12 text-center">
                        <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune publication</h3>
                        <p className="text-gray-600">Créez votre première publication programmée</p>
                    </div>
                ) : viewMode === 'calendar' ? (
                    <CalendarView posts={posts} />
                ) : (
                    <div className="grid gap-4">
                        {posts.map((post) => (
                            <div key={post.id} className="bg-white rounded-lg shadow hover:shadow-md transition p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className="text-2xl">{getPlatformIcon(post.platform)}</span>
                                            <h3 className="text-lg font-semibold text-gray-900">{post.title || 'Sans titre'}</h3>
                                        </div>
                                        <p className="text-gray-600 line-clamp-2">{post.text_content}</p>
                                    </div>
                                    {getStatusBadge(post.status)}
                                </div>

                                <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                                    <div className="flex items-center gap-1">
                                        <Clock size={16} />
                                        <span>{new Date(post.scheduled_at.endsWith('Z') ? post.scheduled_at : post.scheduled_at + 'Z').toLocaleString('fr-FR')}</span>
                                    </div>
                                    {post.image_url && (
                                        <div className="flex items-center gap-1">
                                            <ImageIcon size={16} />
                                            <span>Image incluse</span>
                                        </div>
                                    )}
                                </div>

                                <div className="flex gap-2">
                                    {post.status === 'scheduled' && (
                                        <>
                                            <button
                                                onClick={() => {
                                                    setEditingPost(post);
                                                    setShowModal(true);
                                                }}
                                                className="flex items-center gap-1 px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition text-sm"
                                            >
                                                <Calendar size={16} />
                                                Modifier
                                            </button>
                                            <button
                                                onClick={() => handleSendNow(post.id)}
                                                className="flex items-center gap-1 px-3 py-2 bg-green-50 hover:bg-green-100 text-green-700 rounded-lg transition text-sm"
                                            >
                                                <Send size={16} />
                                                Envoyer
                                            </button>
                                        </>
                                    )}
                                    {/* Bouton Supprimer disponible pour tous les posts */}
                                    <button
                                        onClick={() => handleDelete(post.id)}
                                        className="flex items-center gap-1 px-3 py-2 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg transition text-sm"
                                    >
                                        <Trash2 size={16} />
                                        Supprimer
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {/* Modal de création / modification */}
            {showModal && (
                <CreatePostModal
                    onClose={() => {
                        setShowModal(false);
                        setEditingPost(null);
                    }}
                    onPostCreated={() => {
                        fetchPosts();
                        setShowModal(false);
                        setEditingPost(null);
                    }}
                    initialData={editingPost}
                />
            )}
        </div>
    );
}
