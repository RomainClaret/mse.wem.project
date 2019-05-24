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

  displayStatCategory(tag: any, objet: any) {
    const e = {
      'Year': {'0': 2018, '1': 2018, '2': 2018, '3': 2019, '4': 2019, '5': 2019, '6': 2019, '7': 2019},
      'Month': {'0': '12', '1': '11', '2': '10', '3': '05', '4': '04', '5': '03', '6': '02', '7': '01'},
      'Papers': {'0': 1112, '1': 1310, '2': 483, '3': 345, '4': 1378, '5': 1071, '6': 1206, '7': 1095}
    };
    const stats = [];
    this.barChartLabels = [];
    Object.keys(e.Year).map((key) => {
      stats.push(e.Papers[key]);
      this.barChartLabels.push(e.Month[key] + '.' + e.Year[key]);
    });
    console.log(tag);
    console.log(stats);

    this.statsCategory = [
      {data: stats, label: tag.description},
    ];
  }


  private applyDarkTheme() {
    const color = '#e0e0e0';
    const overrides = {
      legend: {
        labels: {fontColor: color}
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
