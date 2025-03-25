import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { LiveEvent } from '../models/LiveEvent';
import { database } from '../config/firebase';
import { onValue, ref } from 'firebase/database';

const useLiveEventInfo = (playerName?: string) => {
    const [data, setData] = useState<LiveEvent[]>([]);
    const [error, setError] = useState<string>("");
    const [dataSource, setDataSource] = useState<'firebase' | 'api' | 'none'>('none');
    const [backendAwake, setBackendAwake] = useState<boolean>(false);
    const prevData = useRef<LiveEvent[]>([]);
    const apiUrl = process.env.REACT_APP_API_URL;

    const areLiveEventsEqual = (prev: LiveEvent[], current: LiveEvent[]) => {
        if (prev.length !== current.length) return false;
        return true;
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

    // Sort live events by timestamp
    const sortLiveEvents = (liveEvents: LiveEvent[]): LiveEvent[] => {
        return [...liveEvents].sort((a: LiveEvent, b: LiveEvent) => {
            const parseDate = (timestamp: string) => {
                const [datePart, timePart] = timestamp.split(', ');
                const [day, month, year] = datePart.split('/');
                return new Date(`${year}-${month}-${day}T${timePart}`);
            };
            return parseDate(b.timestamp).getTime() - parseDate(a.timestamp).getTime();
        });
    };
    
    // Setup Firebase listener for cached data
    useEffect(() => {
        const firebasePath = `tft-games-history` 
        const liveEventsRef = ref(database, firebasePath);
        
        const unsubscribe = onValue(liveEventsRef, (snapshot) => {
            const firebaseData = snapshot.val();
            if (firebaseData) {
                const liveEvents = Object.values(firebaseData).map((data: any) => {
                    return transform(data.games)
                });
                const sortedEvents = sortLiveEvents(liveEvents);
                
                setData(sortedEvents);
                prevData.current = sortedEvents;
                setDataSource('firebase');
            }
        });
        return () => unsubscribe();
    }, [playerName]);

    // Fetch data from backend API 
    useEffect(() => {
        const fetchFromAPI = async () => {
            try {
                const response = await axios.get(apiUrl + 'live-events', {
                    params: playerName ? { name: playerName } : {}
                });
                
                let liveEvents = response.data.map((data: any) => transform(data));
                liveEvents = sortLiveEvents(liveEvents);
                
                if (!areLiveEventsEqual(prevData.current, liveEvents)) {
                    setData(liveEvents);
                    prevData.current = liveEvents;
                }
                
                setBackendAwake(true);
                setDataSource('api');
                
                if (error !== "") {
                    setError("");
                }
            } catch (err) {
                setBackendAwake(false);
            }
        };
        
        fetchFromAPI();
        const interval = setInterval(() => {
            fetchFromAPI();
        },  10000); 
        
        return () => clearInterval(interval);
    }, [playerName, apiUrl, error, backendAwake]);

    return { 
        data, 
        error,
        isLoading: data.length === 0 && !error,
        dataSource,
        isLive: backendAwake
    };
};

export default useLiveEventInfo;
