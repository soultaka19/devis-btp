import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const token = localStorage.getItem('access_token');
  const lang = localStorage.getItem('btp_language') || 'fr';

  let headers: Record<string, string> = { 'Accept-Language': lang };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const authReq = req.clone({ setHeaders: headers });

  return next(authReq).pipe(
    catchError((error) => {
      if (error.status === 401 && !req.url.includes('/auth/')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.navigate(['/auth/login']);
      }
      return throwError(() => error);
    })
  );
};
