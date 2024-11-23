import { StoredDocument } from "./StoredDocument";

export interface LiveEvent extends StoredDocument{
    player: string;
    rank: string;
    status: 'entered' | 'exited';
    timestamp: string;
    gameInfo?: GameInfo;
}

export interface GameInfo {
    rounds: number;
    result: string;
    newRating: string;
    topComp: string;
    placement: number;
    duration: string;
    augments: Augment[];
}

export interface Augment {
    name: string;
    stars: number;
}