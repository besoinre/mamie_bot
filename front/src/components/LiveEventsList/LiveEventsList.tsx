import React from 'react';
import { LiveEvent } from '../../models/LiveEvent';
import LiveEventCard from '../LiveEventCard/LiveEventCard';
import './LiveEventsList.scss';
import useLiveEventInfo from '../../hooks/useLiveEventInfo';

interface LiveEventsListProps {
    playerName: string;
}

const LiveEventsList: React.FC<LiveEventsListProps> = ({ playerName}) => {
    
    const { data, error } = useLiveEventInfo(playerName);

    if (error) {
        return (
            <div className="live-events">
                <p>{error}</p>
            </div>
        );
    }

    if(data.length === 0){
        return (
            <div className="live-events">
                <p>No data to display</p>
            </div>
        );
    }

    return (
        <div className="live-events">
            {data && data.length > 0 ? (
                data.map((liveEvent: LiveEvent) => (
                    <LiveEventCard
                        key={liveEvent._id}
                        liveEvent={liveEvent}
                    />
                ))
            ) : (
                <p>No current player activity</p>
            )}
        </div>
    );
};

export default LiveEventsList;
