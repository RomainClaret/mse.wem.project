import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {debounceTime, distinctUntilChanged} from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class DataLoaderService {

  constructor(private http: HttpClient) {

  }

  search(valueSearch): Observable<any> {
    return this.http.get<any>(`http://127.0.0.1:5000/api/search/53?page=3`)
      .pipe(debounceTime(200), distinctUntilChanged());
  }
}
