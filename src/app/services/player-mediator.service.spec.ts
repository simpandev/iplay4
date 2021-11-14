import { TestBed } from '@angular/core/testing';

import { PlayerMediatorService } from './player-mediator.service';

describe('PlayerMediatorService', () => {
  let service: PlayerMediatorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PlayerMediatorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
