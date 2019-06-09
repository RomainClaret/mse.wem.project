import {AfterViewInit, Component, OnInit, ViewChild} from '@angular/core';
import {MatPaginator} from '@angular/material';
import {DataLoaderService} from './service/data-loader.service';
import {ChartDataSets, ChartOptions, ChartType} from 'chart.js';
import {Label, ThemeService} from 'ng2-charts';

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

  barChartOptions: ChartOptions = {
    responsive: true,
    scales: {xAxes: [{}], yAxes: [{}]},
  };
  barChartLabels: Label[] = [];
  barChartType: ChartType = 'line';
  barChartLegend = true;
  docStatSelected: any;

  statsCategory: ChartDataSets[] = [];

  constructor(private dataLoaderService: DataLoaderService, private themeService: ThemeService) {
  }

  ngOnInit(): void {
    this.applyDarkTheme();
  }

  search(value) {
    this.page = 0;
    this.textSearch = value;
    this.loadData(value);
  }

  private loadData(value) {
    this.dataLoaderService.search(value, this.pageSize, this.page).subscribe(data => {
      this.data = data.result;
      this.totalResult = data.total;
      document.querySelector('#basic_container').scrollTop = 0;
    });
  }

  displayPaginatorStyle(): string {
    if (this.data.length && this.totalResult > this.data.length) {
      return '';
    }
    return 'hide';
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

  displayAllStatCategory() {
    this.displayStatCategory('Papers', {title: 'All Document'});
  }

  displayCompareCategory() {
    this.dataLoaderService.stat('all', 'AllCat').subscribe((event) => {
      this.docStatSelected = {title: 'Sum categories'};
      const stats = [];
      const result = event.result;
      this.barChartLabels = [];
      this.barChartType = 'bar';
      Object.keys(result)
        .filter(key => ['Year', 'Month', 'Papers'].indexOf(key) < 0)
        .map((key) => {
          const sum = Object.keys(result[key]).map(k => {
            return result[key][k];
          }).reduce((accumulator, currentValue) => accumulator + currentValue, 0);
          stats.push(sum);
          this.barChartLabels.push(key);
        });
      this.statsCategory = [
        {data: stats, label: 'Categories'},
      ];
    });
  }

  displayStatCategory(category: any, objet: any) {
    this.barChartType = 'line';
    this.dataLoaderService.stat(objet.idPage, category).subscribe((event) => {
      this.docStatSelected = objet;
      const stats = [];
      const result = event.result;
      this.barChartLabels = [];
      Object.keys(result.Values)
        .sort((k1, k2) => (result.Year[k1] + result.Month[k1]) - (result.Year[k2] + result.Month[k2]))
        .filter(key => result.Values[key] > 0)
        .map((key) => {
          stats.push(result.Values[key]);
          this.barChartLabels.push(result.Month[key] + '.' + result.Year[key]);
        });
      this.statsCategory = [
        {data: stats, label: category},
      ];
    });
  }

  private applyDarkTheme() {
    const color = '#e0e0e0';
    const overrides = {
      legend: {
        labels: {fontColor: color}
      },
      plugins: {
        datalabels: {
          color: '#ffffff'
        }
      },
      scales: {
        xAxes: [{
          scaleLabel: {
            display: true,
            labelString: ''
          },
          ticks: {
            fontColor: color,
          },
          color: 'rgba(255,255,255,0.1)',
          gridLines: {
            drawBorder: true,
            display: false,
            color: 'rgba(255,255,255,0.1)'
          },
        }],
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: ''
          },
          ticks: {
            fontColor: color,
            min: 0,
          },
          gridLines: {
            display: false,
            color: 'rgba(255,255,255,0.1)'
          }
        }]
      }
    };
    this.themeService.setColorschemesOptions(overrides);
  }
}
