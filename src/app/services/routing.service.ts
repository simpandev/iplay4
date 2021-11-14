import { Injectable } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { take } from 'rxjs/operators';

const PLAYLIST_NAME_PATT = /\/ui\/playlists\/([\w\-]+)\??.*/;

@Injectable({
  providedIn: 'root'
})
export class RoutingService {

  constructor(private router: Router,
              private activatedRoute: ActivatedRoute) { }

  async getPlaylistId(): Promise<string | null> {
    let matcher = this.router.url.match(PLAYLIST_NAME_PATT);
    if (matcher == null || matcher.length <= 0) {
      console.debug('retrieved playlist ID but got undefined');
      return null;
    }
    console.debug(`retrieved playlist ID: ${matcher[1]}`);
    return matcher[1];
  }

  async setPlaylistId(playlistId: string): Promise<void> {
    console.debug(`set playlist ID: ${playlistId}`);
    let queryParams = await this.activatedRoute.queryParams.pipe(take(1)).toPromise();
    await this.router.navigate([`/ui/playlists/${playlistId}`], {
      queryParams: queryParams,
      queryParamsHandling: 'merge'
    });
  }

  async getVideoId(): Promise<string | null> {
    let queryParams = await this.activatedRoute.queryParams.pipe(take(1)).toPromise();
    if (queryParams['video-id'] == null) {
      console.debug('retrieved video ID but got undefined');
      return null;
    }
    console.debug(`retrieved video ID: ${queryParams['video-id']}`);
    return queryParams['video-id'];
  }

  async setVideoId(videoId: string): Promise<void> {
    console.debug('set video ID: ' + videoId);
    this.router.navigate([], {
      relativeTo: this.activatedRoute,
      queryParams: {
        'video-id': videoId
      },
      queryParamsHandling: 'merge'
    });
  }

}
