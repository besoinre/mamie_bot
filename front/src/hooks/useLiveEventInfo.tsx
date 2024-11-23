import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { LiveEvent } from '../models/LiveEvent';

const useLiveEventInfo = (playerName?: string) => {
    const [data, setData] = useState<LiveEvent[]>([]);
    const [error, setError] = useState<string>("");
    const prevData = useRef<LiveEvent[]>([]);

    const areLiveEventsEqual = (prev: LiveEvent[], current: LiveEvent[]) => {
        if (prev.length !== current.length) return false;
        return true
    };

    const transform = (data: any): LiveEvent => {
        const liveEvent: LiveEvent = {
            _id: data._id,
            player: data.player,
            rank: data.rank,
            status: data.status,
            timestamp: data.timestamp,
            gameInfo: data.game_info
                ? {
                      rounds: data.game_info.rounds,
                      result: data.game_info.result,
                      newRating: data.game_info.new_rating,
                      topComp: data.game_info.top_comp,
                      placement: data.game_info.placement,
                      duration: data.game_info.duration,
                      augments: data.game_info.augments
                          ? data.game_info.augments.map((augment: any) => ({
                                name: augment.name,
                                stars: augment.stars,
                            }))
                          : [],
                  }
                : undefined, 
        };
        return liveEvent;
    };
    

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:5000/live-events', {
                    params: playerName ? { name: playerName } : {}
                });
                let liveEvents = response.data.map((data: any) => transform(data));
                liveEvents = liveEvents.sort((a: any, b: any) => {
                    const parseDate = (timestamp: string) => {
                        const [datePart, timePart] = timestamp.split(', ');
                        const [day, month, year] = datePart.split('/');
                        return new Date(`${year}-${month}-${day}T${timePart}`);
                    };
                    return parseDate(b.timestamp).getTime() - parseDate(a.timestamp).getTime();
                });
                if (!areLiveEventsEqual(prevData.current, liveEvents)) {
                    setData(liveEvents);
                    prevData.current = liveEvents;
                }
                if(error !== ""){
                    setError("")
                }
            } catch (err) {
                setError(`Error fetching data : ${err}`);
            } finally {
            }
        };
        const interval = setInterval(fetchData, 10000);
        fetchData();

        return () => clearInterval(interval);
    }, [playerName]);

    return { data, error };
}

export default useLiveEventInfo;
