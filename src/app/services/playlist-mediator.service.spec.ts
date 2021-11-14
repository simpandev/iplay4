import { TestBed } from '@angular/core/testing';

import { PlaylistMediatorService } from './playlist-mediator.service';

describe('PlaylistMediatorService', () => {
  let service: PlaylistMediatorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PlaylistMediatorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
