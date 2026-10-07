with open("frontend/src/api/auth.ts", "r") as f:
    code = f.read()

new_api = """
  forgotPassword: (data: { email: string }) =>
    api.post<{ message: string }>('/auth/forgot-password', data, { requireAuth: false }),

  resetPassword: (data: { email: string; otp_code: string; new_password: string }) =>
    api.post<{ message: string }>('/auth/reset-password', data, { requireAuth: false }),
"""

code = code.replace("logout: () => api.post<void>('/auth/logout'),", "logout: () => api.post<void>('/auth/logout'),\n" + new_api)

with open("frontend/src/api/auth.ts", "w") as f:
    f.write(code)
