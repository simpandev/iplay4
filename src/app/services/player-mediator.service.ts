import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export const NOTHING_TO_DO_COMMAND = 'NOTHING_TO_DO_COMMAND';
export const VIDEO_ID_CHANGED_COMMAND = 'VIDEO_ID_CHANGED_COMMAND';
export const TOGGLE_PLAY_PAUSE_COMMAND = 'TOGGLE_PLAY_PAUSE_COMMAND';
export const REW_5S_COMMAND = 'REW_5S_COMMAND';
export const FFWD_5S_COMMAND = 'FFWD_5S_COMMAND';
export const GO_TO_BEGIN_COMMAND = 'GO_TO_BEGIN_COMMAND';

@Injectable({
  providedIn: 'root'
})
export class PlayerMediatorService {

  private commandSource = new BehaviorSubject<string>(NOTHING_TO_DO_COMMAND);

  command$ = this.commandSource.asObservable();

  notifyVideoIdChanged(): void {
    this.sendCommand(VIDEO_ID_CHANGED_COMMAND);
  }

  togglePlayPause(): void {
    this.sendCommand(TOGGLE_PLAY_PAUSE_COMMAND);
  }

  rew5S(): void {
    this.sendCommand(REW_5S_COMMAND);
  }

  ffwd5S(): void {
    this.sendCommand(FFWD_5S_COMMAND);
  }

  goToBegin(): void {
    this.sendCommand(GO_TO_BEGIN_COMMAND);
  }

  private sendCommand(cmd: string): void {
    this.commandSource.next(cmd);
  }

}
