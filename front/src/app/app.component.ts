import {AfterViewInit, Component, OnInit, ViewChild} from '@angular/core';
import {MatPaginator} from '@angular/material';
import {DataLoaderService} from './service/data-loader.service';
import {ChartDataSets, ChartOptions, ChartType} from 'chart.js';
import {Label, ThemeService} from 'ng2-charts';
import * as pluginDataLabels from 'chartjs-plugin-datalabels';

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
  docStatSelected: string;
  public barChartPlugins = [pluginDataLabels];

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
      this.ngAfterViewInit();
    });
  }

  displayPaginatorStyle(): string {
    if (this.data.length && this.totalResult > this.data.length) {
      return '';
    }
    return 'hide';
  }

  ngAfterViewInit(): void {
    console.log(this.paginator);
    if (this.paginator) {
      console.log('paginator');
      this.paginator.page.subscribe(
        (event) => {
          this.pageSize = event.pageSize;
          this.page = event.pageIndex;
          console.log('ok');
          this.loadData(this.textSearch);
        });
    }
  }

  displayStatCategory(category: any, objet: any) {
    this.dataLoaderService.stat(objet.idPage, category).subscribe((event) => {
      this.docStatSelected = objet;
      const stats = [];
      const result = event.result;
      this.barChartLabels = [];
      Object.keys(result.Year).map((key) => {
        stats.push(result.Papers[key]);
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
