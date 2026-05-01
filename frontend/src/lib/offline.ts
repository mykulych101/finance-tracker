

export function allowCloudSync(allow: boolean): boolean {
  if (allow) {
    sessionStorage.setItem('finance-api-mode', 'true');
  } else {
    sessionStorage.removeItem('finance-api-mode');
  }
  return allow;
}

export function isCloudSyncAllowed(): boolean {
  return sessionStorage.getItem('finance-api-mode') === 'true';
}
