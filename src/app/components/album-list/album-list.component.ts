import { Component, OnInit } from '@angular/core';
import { PlaylistSummary } from '../../dto/PlaylistSummary';
import { AlbumService } from '../../services/album.service';
import { PlaylistMediatorService } from '../../services/playlist-mediator.service';
import { RoutingService } from '../../services/routing.service';

@Component({
  selector: 'app-album-list',
  templateUrl: './album-list.component.html',
  styleUrls: ['./album-list.component.scss']
})
export class AlbumListComponent implements OnInit {

  playlistSummary: PlaylistSummary = {
    favorite: "",
    playlists: []
  };

  selectedIndex: number = -1;

  constructor(private albumService: AlbumService,
              private routingService: RoutingService,
              private playlistMediatorService: PlaylistMediatorService) { }

  async ngOnInit(): Promise<void> {
    let playlistSummary = await this.albumService.getAlbumList();
    this.playlistSummary = playlistSummary;
    let playlistId = await this.routingService.getPlaylistId();
    if (playlistId == null) {
      playlistId = playlistSummary.favorite;
    }
    await this.loadPlaylist(playlistId);
  }

  async onClick(index: number): Promise<void> {
    await this.loadPlaylist(this.playlistSummary.playlists[index].id);
  }

  private async loadPlaylist(playlistId: string): Promise<void> {
    await this.routingService.setPlaylistId(playlistId);
    this.playlistMediatorService.loadPlaylist();
    this.selectedIndex = this.playlistSummary.playlists.map(album => album.id).indexOf(playlistId);
  }

}
