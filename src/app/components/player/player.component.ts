import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { YouTubePlayer } from '@angular/youtube-player';
import { Subscription } from 'rxjs';
import { FFWD_5S_COMMAND, GO_TO_BEGIN_COMMAND, NOTHING_TO_DO_COMMAND, PlayerMediatorService, REW_5S_COMMAND, TOGGLE_PLAY_PAUSE_COMMAND, VIDEO_ID_CHANGED_COMMAND } from '../../services/player-mediator.service';
import { PlaylistMediatorService } from '../../services/playlist-mediator.service';
import { RoutingService } from '../../services/routing.service';

@Component({
  selector: 'app-player',
  templateUrl: './player.component.html',
  styleUrls: ['./player.component.scss']
})
export class PlayerComponent implements OnInit, OnDestroy {

  videoId?: string | null;

  @ViewChild('youtube_player')
  private youtubePlayer!: YouTubePlayer;

  private playerMediatorServiceSubscription?: Subscription;

  constructor(private routingService: RoutingService,
              private playerMediatorService: PlayerMediatorService,
              private playlistMediatorService: PlaylistMediatorService) { }

  async ngOnInit() {
    await this.initHTML();
    await this.initCommands();
    await this.initStateObserver();
    await this.onChangeVideoId();
  }

  ngOnDestroy(): void {
    this.playerMediatorServiceSubscription?.unsubscribe();
  }

  private async initHTML(): Promise<void> {
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    document.body.appendChild(tag);
  }

  private async initCommands(): Promise<void> {
    this.playerMediatorServiceSubscription = this.playerMediatorService.command$.subscribe(cmd => {
      switch (cmd) {
        case VIDEO_ID_CHANGED_COMMAND:
          this.onChangeVideoId();
          break;
        case TOGGLE_PLAY_PAUSE_COMMAND:
          this.onTogglePlayPause();
          break;
        case REW_5S_COMMAND:
          this.rew(5);
          break;
        case FFWD_5S_COMMAND:
          this.ffwd(5);
          break;
        case GO_TO_BEGIN_COMMAND:
          this.goToBegin();
          break;
        case NOTHING_TO_DO_COMMAND:
        default:
          // do nothing
      }
    });
  }

  private async initStateObserver(): Promise<void> {
    // ATTENTION! this.youtubePlayer.stateChange.subscribe(onStateChangeEvent => {}); - DOES NOT WORK
    setInterval(() => {
      switch (this.youtubePlayer.getPlayerState()) {
        case YT.PlayerState.CUED:
          this.youtubePlayer.playVideo();
          break;
        case YT.PlayerState.ENDED:
          this.playlistMediatorService.notifyVideoEnded();
          break;
        case YT.PlayerState.PLAYING:
        case YT.PlayerState.UNSTARTED:
        case YT.PlayerState.PAUSED:
        case YT.PlayerState.BUFFERING:
        default:
          // do nothing
      }
    }, 1000)
  }

  private async onChangeVideoId(): Promise<void> {
    this.videoId = await this.routingService.getVideoId();
  }

  private onTogglePlayPause(): void {
    const playerState = this.youtubePlayer.getPlayerState();
    switch (playerState) {
      case YT.PlayerState.PLAYING:
        this.youtubePlayer.pauseVideo();
        break;
      case YT.PlayerState.UNSTARTED:
      case YT.PlayerState.PAUSED:
      case YT.PlayerState.CUED:
        this.youtubePlayer.playVideo();
        break;
      case YT.PlayerState.ENDED:
      case YT.PlayerState.BUFFERING:
      default:
        // do nothing
    }
  }

  private rew(dt: number): void {
    const currentTime = this.youtubePlayer.getCurrentTime();
    const futureTime = (currentTime - dt <= 0) ? 0 : currentTime - dt;
    this.youtubePlayer.seekTo(futureTime, true);
  }

  private ffwd(dt: number): void {
    const currentTime = this.youtubePlayer.getCurrentTime();
    const duration = this.youtubePlayer.getDuration();
    const futureTime = (currentTime + dt >= duration) ? duration : currentTime + dt;
    this.youtubePlayer.seekTo(futureTime, true);
  }

  private goToBegin(): void {
    this.youtubePlayer.seekTo(0, true);
  }

}
