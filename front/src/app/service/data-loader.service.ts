import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {debounceTime, distinctUntilChanged} from 'rxjs/operators';
import {environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DataLoaderService {

  constructor(private http: HttpClient) {

  }

  search(valueSearch): Observable<any> {
    return this.http.get<any>(`${environment.server}/api/search/53?page=3`)
      .pipe(debounceTime(200), distinctUntilChanged());
  }

  stat(idDocument, categorie): Observable<any> {
    return this.http.get<any>(`${environment.server}/api/stat/idDocument/category`)
      .pipe(debounceTime(200), distinctUntilChanged());
  }
}
