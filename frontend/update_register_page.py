import os

with open("src/pages/Register/RegisterPage.tsx", "r") as f:
    content = f.read()

# Replace the useAuth register with authApi register
content = content.replace(
    "import { useAuth } from '../../store/AuthContext';",
    "import { useAuth } from '../../store/AuthContext';\nimport { authApi } from '../../api/auth';\nimport { setTokens } from '../../api/client';"
)

content = content.replace(
    "const [loading, setLoading] = useState(false);",
    "const [loading, setLoading] = useState(false);\n  const [showOtp, setShowOtp] = useState(false);\n  const [otpCode, setOtpCode] = useState('');"
)

new_handle_submit = """
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;

    setLoading(true);
    try {
      await authApi.register({
        email: email.trim(),
        password,
        display_name: displayName.trim() || undefined,
      });
      setShowOtp(true);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!otpCode.trim()) return;
    
    setLoading(true);
    try {
      const tokens = await authApi.verifyOtp({
        email: email.trim(),
        otp_code: otpCode.trim(),
      });
      setTokens(tokens.access_token, tokens.refresh_token);
      window.location.href = '/dashboard';
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Verification failed.');
    } finally {
      setLoading(false);
    }
  };
"""
import re
content = re.sub(r'const handleSubmit = async.*?};', new_handle_submit.strip(), content, flags=re.DOTALL)

otp_form = """
            {showOtp ? (
              <form onSubmit={handleVerifyOtp} noValidate className="space-y-4">
                <div className="mb-4">
                  <h2 className="text-[18px] font-semibold text-stone-900">Verify your email</h2>
                  <p className="text-[14px] text-stone-500 mt-1">
                    We just sent a 6-digit code to {email}. Please enter it below.
                  </p>
                </div>
                {apiError && <InlineError message={apiError} />}
                <Input
                  label="Verification Code"
                  type="text"
                  placeholder="123456"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  required
                />
                <Button type="submit" fullWidth size="lg" loading={loading} className="mt-2">
                  Verify & Sign in
                </Button>
              </form>
            ) : (
              <form onSubmit={handleSubmit} noValidate className="space-y-4">
"""

content = content.replace('<form onSubmit={handleSubmit} noValidate className="space-y-4">', otp_form)
content = content.replace('</form>', '</form>\n            )}')

with open("src/pages/Register/RegisterPage.tsx", "w") as f:
    f.write(content)

print("Updated RegisterPage.tsx")
