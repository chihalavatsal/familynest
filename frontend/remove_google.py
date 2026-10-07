import re

# Fix LoginPage.tsx
with open("frontend/src/pages/Login/LoginPage.tsx", "r") as f:
    login = f.read()

# Match the "Or continue with" divider and the Google button up to </Button>
login = re.sub(r'<div className="relative my-4">.*?Google\n              </Button>', '', login, flags=re.DOTALL)

with open("frontend/src/pages/Login/LoginPage.tsx", "w") as f:
    f.write(login)

# Fix RegisterPage.tsx
with open("frontend/src/pages/Register/RegisterPage.tsx", "r") as f:
    register = f.read()

register = re.sub(r'<div className="relative my-4">.*?Google\n              </Button>', '', register, flags=re.DOTALL)

# Add Resend OTP button
resend_code = """
  const handleResendOtp = async () => {
    if (!email.trim()) return;
    try {
      await authApi.resendOtp({ email: email.trim() });
      setApiError(null);
      // Could show a success toast here
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Failed to resend code.');
    }
  };
"""
register = register.replace("const handleVerifyOtp = async (e: React.FormEvent) => {", resend_code + "\n  const handleVerifyOtp = async (e: React.FormEvent) => {")

resend_btn = """
                <Button type="submit" fullWidth size="lg" loading={loading} className="mt-2">
                  Verify & Sign in
                </Button>
                
                <div className="text-center mt-3">
                  <button type="button" onClick={handleResendOtp} className="text-[13px] text-[#92614a] font-medium hover:underline">
                    Didn't receive a code? Resend
                  </button>
                </div>
"""
register = register.replace('<Button type="submit" fullWidth size="lg" loading={loading} className="mt-2">\n                  Verify & Sign in\n                </Button>', resend_btn)

with open("frontend/src/pages/Register/RegisterPage.tsx", "w") as f:
    f.write(register)
