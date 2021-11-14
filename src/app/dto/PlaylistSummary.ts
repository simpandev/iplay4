import { Album } from "./Album";

export interface PlaylistSummary {
    favorite: string;
    playlists: Album[];
}