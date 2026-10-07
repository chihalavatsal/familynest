with open("frontend/src/api/auth.ts", "r") as f:
    code = f.read()

new_api = """
  resendOtp: (data: { email: string }) =>
    api.post<{ message: string }>('/auth/resend-otp', data, { requireAuth: false }),
"""

code = code.replace("logout: () => api.post<void>('/auth/logout'),", "logout: () => api.post<void>('/auth/logout'),\n" + new_api)

with open("frontend/src/api/auth.ts", "w") as f:
    f.write(code)
