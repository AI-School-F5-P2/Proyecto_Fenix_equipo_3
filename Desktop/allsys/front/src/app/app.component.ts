import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from "./layout/components/navbar/navbar.component";
import { LayoutComponent } from "./layout/layout.component";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NavbarComponent, LayoutComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'front';
}
