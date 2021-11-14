import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export const NOTHING_TO_DO_COMMAND = 'NOTHING_TO_DO_COMMAND';
export const LOAD_PLAYLIST_COMMAND = 'LOAD_PLAYLIST_COMMAND';
export const SELECT_FIRST_VIDEO_COMMAND = 'SELECT_FIRST_VIDEO_COMMAND';
export const SELECT_LAST_VIDEO_COMMAND = 'SELECT_LAST_VIDEO_COMMAND';
export const SELECT_NEXT_VIDEO_COMMAND = 'SELECT_NEXT_VIDEO_COMMAND';
export const SELECT_5_NEXT_VIDEO_COMMAND = 'SELECT_5_NEXT_VIDEO_COMMAND';
export const SELECT_PREV_VIDEO_COMMAND = 'SELECT_PREV_VIDEO_COMMAND';
export const SELECT_5_PREV_VIDEO_COMMAND = 'SELECT_5_PREV_VIDEO_COMMAND';
export const PLAY_SELECTED_VIDEO_COMMAND = 'PLAY_SELECTED_VIDEO_COMMAND';
export const VIDEO_ENDED_COMMAND = 'VIDEO_ENDED_COMMAND';

@Injectable({
  providedIn: 'root'
})
export class PlaylistMediatorService {

  private commandSource = new BehaviorSubject<string>(NOTHING_TO_DO_COMMAND);

  command$ = this.commandSource.asObservable();

  loadPlaylist(): void {
    this.sendCommand(LOAD_PLAYLIST_COMMAND);
  }

  selectFirstVideo(): void {
    this.sendCommand(SELECT_FIRST_VIDEO_COMMAND);
  }

  selectLastVideo(): void {
    this.sendCommand(SELECT_LAST_VIDEO_COMMAND);
  }

  selectNextVideo(): void {
    this.sendCommand(SELECT_NEXT_VIDEO_COMMAND);
  }

  select5NextVideo(): void {
    this.sendCommand(SELECT_5_NEXT_VIDEO_COMMAND);
  }

  selectPrevVideo(): void {
    this.sendCommand(SELECT_PREV_VIDEO_COMMAND);
  }

  select5PrevVideo(): void {
    this.sendCommand(SELECT_5_PREV_VIDEO_COMMAND);
  }

  playSelectedVideo(): void {
    this.sendCommand(PLAY_SELECTED_VIDEO_COMMAND);
  }

  notifyVideoEnded(): void {
    this.sendCommand(VIDEO_ENDED_COMMAND);
  }

  private sendCommand(cmd: string): void {
    this.commandSource.next(cmd);
  }
  
}
