const fs = require('fs');
const file = 'src/api/auth.ts';
let code = fs.readFileSync(file, 'utf8');

const verifyFunc = `
  verifyOtp: (data: { email: string; otp_code: string }) =>
    api.post<AuthResponse>('/auth/verify-otp', data),
`;

code = code.replace(/logout: \(\) => api\.post\('\/auth\/logout'\),/g, `logout: () => api.post('/auth/logout'),\n${verifyFunc}`);

fs.writeFileSync(file, code);
