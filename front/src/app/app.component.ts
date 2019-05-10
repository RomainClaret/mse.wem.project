import {AfterViewInit, Component, OnInit, ViewChild} from '@angular/core';
import {MatPaginator} from '@angular/material';
import {DataLoaderService} from './service/data-loader.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, AfterViewInit {

  @ViewChild(MatPaginator) paginator: MatPaginator;
  data: any[] = [];
  totalResult = 0;
  page = 0;
  textSearch: string;
  pageSize = 10;

  constructor(private dataLoaderService: DataLoaderService) {
  }

  ngOnInit(): void {
  }

  search(value) {
    this.page = 0;
    this.textSearch = value;
    this.loadData(value);
  }

  private loadData(value) {
    this.dataLoaderService.search(value).subscribe(data => {
      this.data = data.result;
      this.totalResult = data.total;
    });
  }

  ngAfterViewInit(): void {
    if (this.paginator) {
      this.paginator.page.subscribe(
        (event) => {
          this.pageSize = event.pageSize;
          this.page = event.pageIndex;
          this.loadData(this.textSearch);
        });
    }
  }
}
