import request from './request'

export function login(username: string, password: string) {
  return request.post('/auth/login', { username, password })
}

export function register(username: string, password: string) {
  return request.post('/auth/register', { username, password })
}

export function getMe() {
  return request.get('/auth/me')
}
