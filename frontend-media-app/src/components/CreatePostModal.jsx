import { useState } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import { X, Upload, Image as ImageIcon, Loader } from 'lucide-react';
import api from '../api';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function CreatePostModal({ onClose, onPostCreated, initialData = null }) {
    const [title, setTitle] = useState(initialData?.title || '');
    const [content, setContent] = useState(initialData?.text_content || '');
    const [platform, setPlatform] = useState(initialData?.platform || 'linkedin');
    const [scheduledDate, setScheduledDate] = useState(initialData ? new Date(initialData.scheduled_at) : new Date());
    const [image, setImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(initialData?.image_url || null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImage(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            let imageUrl = initialData?.image_url || null;

            // 1. Upload Image if new image selected
            if (image) {
                const formData = new FormData();
                formData.append('files', image);
                formData.append('platform', platform);

                const uploadResponse = await api.post('/posts/upload', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                imageUrl = uploadResponse.data.image_url;
            }

            // 2. Create or Update Post
            // Formater la date en conservant le fuseau horaire local (évite le décalage UTC)
            const year = scheduledDate.getFullYear();
            const month = String(scheduledDate.getMonth() + 1).padStart(2, '0');
            const day = String(scheduledDate.getDate()).padStart(2, '0');
            const hours = String(scheduledDate.getHours()).padStart(2, '0');
            const minutes = String(scheduledDate.getMinutes()).padStart(2, '0');
            const seconds = String(scheduledDate.getSeconds()).padStart(2, '0');
            const localDateTime = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;

            const postData = {
                title,
                text_content: content,
                platform,
                scheduled_at: localDateTime,
                image_url: imageUrl,
            };

            if (initialData) {
                await api.put(`/posts/${initialData.id}`, postData);
            } else {
                await api.post('/posts/', postData);
            }

            onPostCreated();
            onClose();
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || 'Erreur lors de l\'enregistrement');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center p-6 border-b">
                    <h2 className="text-xl font-bold text-gray-900">
                        {initialData ? 'Modifier la publication' : 'Nouvelle Publication'}
                    </h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <X size={24} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {error && (
                        <div className="bg-red-50 text-red-700 p-4 rounded-lg text-sm">
                            {error}
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Left Column: Content */}
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Titre (Optionnel)</label>
                                <input
                                    type="text"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                                    placeholder="Titre du post..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Contenu</label>
                                <textarea
                                    value={content}
                                    onChange={(e) => setContent(e.target.value)}
                                    required
                                    rows={6}
                                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                                    placeholder="Rédigez votre post ici..."
                                />
                            </div>
                        </div>

                        {/* Right Column: Settings & Image */}
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Plateforme</label>
                                <select
                                    value={platform}
                                    onChange={(e) => setPlatform(e.target.value)}
                                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                                >
                                    <option value="linkedin">LinkedIn</option>
                                    <option value="instagram">Instagram</option>
                                    <option value="facebook">Facebook</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Date de publication</label>
                                <DatePicker
                                    selected={scheduledDate}
                                    onChange={(date) => setScheduledDate(date)}
                                    showTimeSelect
                                    timeFormat="HH:mm"
                                    timeIntervals={15}
                                    dateFormat="dd/MM/yyyy HH:mm"
                                    locale={fr}
                                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Image</label>
                                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:bg-gray-50 transition cursor-pointer relative">
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleImageChange}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    />
                                    {imagePreview ? (
                                        <div className="relative">
                                            <img src={imagePreview} alt="Preview" className="max-h-40 mx-auto rounded" />
                                            <button
                                                type="button"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    setImage(null);
                                                    setImagePreview(null);
                                                }}
                                                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                                            >
                                                <X size={12} />
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="text-gray-500">
                                            <ImageIcon className="mx-auto h-8 w-8 mb-2" />
                                            <span className="text-sm">Cliquez pour ajouter une image</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-4 border-t">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
                        >
                            Annuler
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
                        >
                            {loading ? <Loader className="animate-spin" size={20} /> : <Upload size={20} />}
                            <span>{initialData ? 'Mettre à jour' : 'Programmer'}</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
