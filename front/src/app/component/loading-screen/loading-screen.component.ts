import {Component, EventEmitter, OnDestroy, OnInit, Output} from '@angular/core';
import {Subscription} from 'rxjs';
import {LoadingScreenService} from '../../service/loading-screen.service';
import {debounceTime} from 'rxjs/operators';

@Component({
  selector: 'app-loading-screen',
  templateUrl: './loading-screen.component.html',
  styleUrls: ['./loading-screen.component.css']
})
export class LoadingScreenComponent implements OnInit, OnDestroy {

  loading = false;
  loadingSubscription: Subscription;
  @Output() lodingEvent = new EventEmitter<boolean>();

  constructor(private loadingScreenService: LoadingScreenService) {
  }

  ngOnInit() {
    this.loadingSubscription = this.loadingScreenService.loadingStatus.pipe(
      debounceTime(200)
    ).subscribe((value) => {
      this.loading = value;
      this.lodingEvent.emit(value);
    });
  }

  ngOnDestroy() {
    this.loadingSubscription.unsubscribe();
  }
}
