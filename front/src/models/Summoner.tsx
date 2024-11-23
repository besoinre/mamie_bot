import { StoredDocument } from "./StoredDocument";

export interface Summoner extends StoredDocument{
    gameName: string,
    tag: string,
    puuid: string
}