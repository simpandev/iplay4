import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PlaylistComponent } from './components/playlist/playlist.component';

const routes: Routes = [
  {
    path: "ui",
    children: [
      {
        path: "playlists", 
        children: [
          {
            path: ":playlist_name", 
            component: PlaylistComponent
          }
        ]
      }
    ] 
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
