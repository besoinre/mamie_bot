import React from 'react';
import './LiveEventCard.scss';
import { LiveEvent } from '../../models/LiveEvent';

interface LiveEventCardProps {
    liveEvent: LiveEvent | undefined;
}

const hasGameInfo = (event: LiveEvent): event is LiveEvent & { gameInfo: NonNullable<LiveEvent['gameInfo']> } => {
    return event.status === 'exited' && event.gameInfo !== undefined;
};

const LiveEventCard: React.FC<LiveEventCardProps> = ({ liveEvent }) => {

    if (!liveEvent) return <></>;

    if (liveEvent.status === 'entered') {
        return (
            <div className="live-event-card">
                <h3 className="header">{liveEvent.player} just got into a game!</h3>
                <div className='details'>
                    <div className='details-column'>
                        <p className='details-header'>Rank</p>
                        <p>{liveEvent.rank}</p>
                    </div>
                </div>
                <small className='timestamp'>{liveEvent.timestamp}</small>
            </div>
        )
    }

    if (liveEvent.status === 'exited' && hasGameInfo(liveEvent))
        return (
            <div className="live-event-card">
                <h3 className="header">{liveEvent.player} just got out of a {liveEvent.gameInfo.rounds} rounds and {liveEvent.gameInfo.duration} game!</h3>
                <p>New rank {liveEvent.gameInfo.newRating}</p>
                {/* <p>The top comp was {liveEvent.gameInfo.topComp}</p> */}
                <div className='details'>
                    <div className='details-column'>
                        <p className='details-header'>Rank</p>
                        <p>{liveEvent.rank}</p>
                    </div>
                    <div className='details-column'>
                        <p className='details-header'>Placement</p>
                        <p>{liveEvent.gameInfo.placement}</p>
                    </div>
                    {/* <div className='details-column'>
                        <p className='details-header'>Augments</p>
                        <ul>
                            {liveEvent.gameInfo.augments.map((augment, index) => (
                                <li key={index}>
                                    {augment.name} ({'★'.repeat(augment.stars)})
                                </li>
                            ))}
                        </ul>
                    </div> */}
                </div>
                <small className='timestamp'>{liveEvent.timestamp}</small>
            </div >
        )
    else
        return <>
            <p>Fail to display : {JSON.stringify(liveEvent)}</p>
        </>
};

export default LiveEventCard;
