import { Component, HostListener } from '@angular/core';
import { PlaylistMediatorService } from './services/playlist-mediator.service';
import { PlayerMediatorService } from './services/player-mediator.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  constructor(private playlistMediatorService: PlaylistMediatorService,
              private playerMediatorService: PlayerMediatorService) {}

  @HostListener('window:keydown', ['$event'])
  keyDownEventListener(event: KeyboardEvent) {
    switch (event.key) {
      case 'Up': // IE/Edge specific value
      case 'ArrowUp':
        event.preventDefault();
        this.playlistMediatorService.selectPrevVideo();
        break;
      case 'Down': // IE/Edge specific value
      case 'ArrowDown':
        event.preventDefault();
        this.playlistMediatorService.selectNextVideo();
        break;
      case 'PageUp':
        event.preventDefault();
        this.playlistMediatorService.select5PrevVideo();
        break;
      case 'PageDown':
        event.preventDefault();
        this.playlistMediatorService.select5NextVideo();
        break;
      default:
        // do nothing
    }
  }

  @HostListener('window:keyup', ['$event'])
  keyUpEventListener(event: KeyboardEvent) {
    switch (event.key) {
      case 'Enter':
        event.preventDefault();
        this.playlistMediatorService.playSelectedVideo();
        break;
      case ' ':
        event.preventDefault();
        this.playerMediatorService.togglePlayPause();
        break;
      case 'Left': // IE/Edge specific value
      case 'ArrowLeft':
        event.preventDefault();
        this.playerMediatorService.rew5S();
        break;
      case 'Right': // IE/Edge specific value
      case 'ArrowRight':
        event.preventDefault();
        this.playerMediatorService.ffwd5S();
        break;
      case 'Home':
        event.preventDefault();
        this.playlistMediatorService.selectFirstVideo();
        break;
      case 'End':
        event.preventDefault();
        this.playlistMediatorService.selectLastVideo();
        break;
      case '0':
        event.preventDefault();
        this.playerMediatorService.goToBegin();
        break;
      default:
        // do nothing
    }
  }
  
}
