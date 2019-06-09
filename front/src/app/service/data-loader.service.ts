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

  search(valueSearch, pageSize, page): Observable<any> {
    return this.http.get<any>(`${environment.server}/api/search/${valueSearch}?page=${page}&pageSize=${pageSize}`)
      .pipe(debounceTime(200), distinctUntilChanged());
  }

  stat(idDocument, category): Observable<any> {
    return this.http.get<any>(`${environment.server}/api/stat/${idDocument}/${category}`)
      .pipe(debounceTime(200), distinctUntilChanged());
  }
}
