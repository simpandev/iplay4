import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { PlaylistSummary } from '../dto/PlaylistSummary';
import { Video } from '../dto/Video';

@Injectable({
  providedIn: 'root'
})
export class AlbumService {

  constructor(private http: HttpClient) { }

  public async getAlbumList(): Promise<PlaylistSummary> {
    return this.http.get<PlaylistSummary>("/playlists/index").toPromise();
  }

  public async getPlaylist(playlistName: string): Promise<Video[]> {
    return this.http.get<Video[]>("/playlists/" + playlistName).toPromise();
  }
}
