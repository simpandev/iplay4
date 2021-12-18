import { Component, ElementRef, OnDestroy, OnInit, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { MatSidenavContent } from '@angular/material/sidenav';
import { MatTableDataSource } from '@angular/material/table';
import { Subscription } from 'rxjs';
import { Video } from '../../dto/Video';
import { AlbumService } from '../../services/album.service';
import { PlayerMediatorService } from '../../services/player-mediator.service';
import { LOAD_PLAYLIST_COMMAND, VIDEO_ENDED_COMMAND, PlaylistMediatorService, PLAY_SELECTED_VIDEO_COMMAND, SELECT_5_NEXT_VIDEO_COMMAND, SELECT_5_PREV_VIDEO_COMMAND, SELECT_FIRST_VIDEO_COMMAND, SELECT_LAST_VIDEO_COMMAND, SELECT_NEXT_VIDEO_COMMAND, SELECT_PREV_VIDEO_COMMAND, NOTHING_TO_DO_COMMAND } from '../../services/playlist-mediator.service';
import { RoutingService } from '../../services/routing.service';

@Component({
  selector: 'app-playlist',
  templateUrl: './playlist.component.html',
  styleUrls: ['./playlist.component.scss']
})
export class PlaylistComponent implements OnInit, OnDestroy {

  displayedColumns: string[] = ['title', 'author', 'duration', 'video_id'];
  dataSource = new MatTableDataSource<Video>([]);

  selectedIndex: number = -1;
  playingIndex: number = -1;

  private playlistMediatorServiceSubscription?: Subscription;

  @ViewChildren('playlistRowView', { read: ElementRef })
  private playlistRowViews!: QueryList<ElementRef>;

  @ViewChild('playlist_header', { read: ElementRef })
  private playlistTableHeader!: ElementRef;

  constructor(private albumService: AlbumService,
              private routingService: RoutingService,
              private playlistMediatorService: PlaylistMediatorService,
              private playerMediatorService: PlayerMediatorService,
              private sideNavContent: MatSidenavContent) { }

  ngOnInit(): void {
    this.initCommands();
  }

  ngOnDestroy(): void {
    this.playlistMediatorServiceSubscription?.unsubscribe();
  }

  select(rowIndex: number): void {
    this.selectedIndex = rowIndex;
    this.scrollPlaylist(rowIndex);
  }

  selectPrev(delta?: number): void {
    delta = (delta != null) ? delta : 1;
    const futureIndex = this.selectedIndex - delta;
    this.select((futureIndex <= 0) ? 0 : futureIndex);
  }

  selectNext(delta?: number): void {
    delta = (delta != null) ? delta : 1;
    const lastIndex = this.dataSource.data.length - 1;
    const futureIndex = this.selectedIndex + delta;
    this.select((futureIndex > lastIndex) ? lastIndex : futureIndex);
  }

  playSelected(): void {
    this.playingIndex = this.selectedIndex;
    this.playVideo();
  }

  private initCommands(): void {
    this.playlistMediatorServiceSubscription = this.playlistMediatorService.command$.subscribe(cmd => {
      switch (cmd) {
        case LOAD_PLAYLIST_COMMAND:
          this.routingService.getPlaylistId()
            .then(playlistId => this.loadPlaylist(playlistId));
          break;
        case SELECT_FIRST_VIDEO_COMMAND:
          this.select(0);
          break;
        case SELECT_LAST_VIDEO_COMMAND:
          this.select(this.dataSource.data.length - 1);
          break;
        case SELECT_NEXT_VIDEO_COMMAND:
          this.selectNext();
          break;
        case SELECT_PREV_VIDEO_COMMAND:
          this.selectPrev();
          break;
        case SELECT_5_NEXT_VIDEO_COMMAND:
          this.selectNext(5);
          break;
        case SELECT_5_PREV_VIDEO_COMMAND:
          this.selectPrev(5);
          break;
        case PLAY_SELECTED_VIDEO_COMMAND:
          this.playSelected();
          break;
        case VIDEO_ENDED_COMMAND:
          this.onVideoEnded();
          break;
        case NOTHING_TO_DO_COMMAND:
        default:
          // do nothing;
      }
    });
  }

  private async loadPlaylist(playlistName: string | null): Promise<void> {
    if (playlistName == null) {
      console.debug('no playlist loading because playlist name is undefined');
      return;
    }
    console.debug(`loading playlist: ${playlistName}`);
    let videos = await this.albumService.getPlaylist(playlistName);
    this.resetStatus();
    this.dataSource.data = videos;
    if (videos.length > 0) {
      this.select(0);
    }
    let videoId = await this.routingService.getVideoId();
    for (let i = 0; i < this.dataSource.data.length; i++) {
      if (videoId === this.dataSource.data[i].video_id) {
        this.playingIndex = i;
        break;
      }
    }
  }

  private resetStatus(): void {
    this.selectedIndex = -1;
    this.playingIndex = -1;
  }

  private async playVideo(): Promise<void> {
    await this.routingService.setVideoId(this.dataSource.data[this.playingIndex].video_id);
    this.playerMediatorService.notifyVideoIdChanged();
  }

  private onVideoEnded(): void {
    if (this.playingIndex < this.dataSource.data.length) {
      this.playingIndex = (this.playingIndex < 0) ? 0 : this.playingIndex + 1;
      this.scrollPlaylist(this.playingIndex);
      this.playVideo();
    }
  }

  private scrollPlaylist(rowIndex: number): void {
    const index = rowIndex.toString();
    const row = this.playlistRowViews.find(r => r.nativeElement.getAttribute('index') === index);

    const scrollFromTop: number = this.sideNavContent.measureScrollOffset("top");
    const rowHeight: number = row?.nativeElement.getBoundingClientRect().height;
    const rowTop: number = rowHeight * rowIndex;
    if (rowTop < scrollFromTop) {
      this.sideNavContent.scrollTo({top: rowTop});
      return;
    }
    
    const viewportHeight: number = window.innerHeight;
    const tableHeaderHeight: number = this.playlistTableHeader?.nativeElement.getBoundingClientRect().height;
    const rowBottom: number = rowTop + rowHeight + tableHeaderHeight;
    if (rowBottom > scrollFromTop + viewportHeight) {
      this.sideNavContent.scrollTo({top: rowBottom - viewportHeight});
    }
  }

}
