import { useState } from 'react';
import {
    format,
    startOfMonth,
    endOfMonth,
    startOfWeek,
    endOfWeek,
    eachDayOfInterval,
    isSameMonth,
    isSameDay,
    addMonths,
    subMonths
} from 'date-fns';
import { fr } from 'date-fns/locale';
import { ChevronLeft, ChevronRight, Image as ImageIcon } from 'lucide-react';

export default function CalendarView({ posts }) {
    const [currentDate, setCurrentDate] = useState(new Date());

    const nextMonth = () => setCurrentDate(addMonths(currentDate, 1));
    const prevMonth = () => setCurrentDate(subMonths(currentDate, 1));

    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(monthStart, { locale: fr });
    const endDate = endOfWeek(monthEnd, { locale: fr });

    const dateFormat = "d";
    const days = eachDayOfInterval({ start: startDate, end: endDate });

    const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

    const getPlatformIcon = (platform) => {
        const icons = {
            linkedin: '💼',
            instagram: '📷',
            facebook: '👥',
        };
        return icons[platform] || '📱';
    };

    const getStatusColor = (status) => {
        const colors = {
            scheduled: 'bg-blue-100 text-blue-800 border-blue-200',
            sent: 'bg-green-100 text-green-800 border-green-200',
            failed: 'bg-red-100 text-red-800 border-red-200',
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    return (
        <div className="bg-white rounded-xl shadow overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
                <h2 className="text-lg font-bold text-gray-900 capitalize">
                    {format(currentDate, 'MMMM yyyy', { locale: fr })}
                </h2>
                <div className="flex gap-2">
                    <button onClick={prevMonth} className="p-2 hover:bg-gray-100 rounded-full">
                        <ChevronLeft size={20} />
                    </button>
                    <button onClick={nextMonth} className="p-2 hover:bg-gray-100 rounded-full">
                        <ChevronRight size={20} />
                    </button>
                </div>
            </div>

            {/* Days Header */}
            <div className="grid grid-cols-7 bg-gray-50 border-b">
                {weekDays.map((day) => (
                    <div key={day} className="py-2 text-center text-sm font-semibold text-gray-600">
                        {day}
                    </div>
                ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 auto-rows-fr">
                {days.map((day, dayIdx) => {
                    const dayPosts = posts.filter(post =>
                        isSameDay(new Date(post.scheduled_at), day)
                    );

                    return (
                        <div
                            key={day.toString()}
                            className={`min-h-[120px] p-2 border-b border-r ${!isSameMonth(day, monthStart) ? 'bg-gray-50 text-gray-400' : 'bg-white'
                                } ${dayIdx % 7 === 6 ? 'border-r-0' : ''}`}
                        >
                            <div className="flex justify-between items-start">
                                <span className={`text-sm font-medium ${isSameDay(day, new Date()) ? 'bg-indigo-600 text-white w-6 h-6 rounded-full flex items-center justify-center' : ''
                                    }`}>
                                    {format(day, dateFormat)}
                                </span>
                                {dayPosts.length > 0 && (
                                    <span className="text-xs text-gray-500 font-medium">
                                        {dayPosts.length} pub{dayPosts.length > 1 ? 's' : ''}
                                    </span>
                                )}
                            </div>

                            <div className="mt-2 space-y-1">
                                {dayPosts.map((post) => (
                                    <div
                                        key={post.id}
                                        className={`text-xs p-1.5 rounded border mb-1 truncate cursor-pointer hover:opacity-80 transition ${getStatusColor(post.status)}`}
                                        title={`${post.title || 'Sans titre'} - ${format(new Date(post.scheduled_at), 'HH:mm')}`}
                                    >
                                        <div className="flex items-center gap-1">
                                            <span>{getPlatformIcon(post.platform)}</span>
                                            <span className="font-medium">{format(new Date(post.scheduled_at), 'HH:mm')}</span>
                                        </div>
                                        <div className="truncate mt-0.5">
                                            {post.title || post.text_content}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
