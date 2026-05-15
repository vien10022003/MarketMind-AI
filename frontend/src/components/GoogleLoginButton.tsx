// React is auto-imported in React 19+
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { authService } from '../services/authService';

interface GoogleLoginButtonProps {
  onSuccess: () => void;
  onError?: (error: string) => void;
}

interface DecodedToken {
  email: string;
  name: string;
  picture?: string;
}

export default function GoogleLoginButton({
  onSuccess,
  onError,
}: GoogleLoginButtonProps) {
  const handleGoogleLogin = async (credentialResponse: any) => {
    try {
      const token = credentialResponse.credential;
      
      // Decode the JWT to get user info
      const decoded = jwtDecode<DecodedToken>(token);
      
      // Send token to backend
      await authService.loginWithGoogle(token, decoded.name);
      
      onSuccess();
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Google login failed';
      console.error('Google login error:', error);
      onError?.(errorMsg);
    }
  };

  const handleGoogleError = () => {
    const errorMsg = 'Google login failed';
    console.error('Google login error');
    onError?.(errorMsg);
  };

  // Get Google Client ID from environment or window object
  const googleClientId = 
    import.meta.env.VITE_GOOGLE_CLIENT_ID ||
    (window as any).GOOGLE_CLIENT_ID ||
    '';

  if (!googleClientId) {
    return (
      <div className="google-login-disabled">
        <p>Google login is not configured. Please set VITE_GOOGLE_CLIENT_ID.</p>
      </div>
    );
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <div className="google-login-button">
        <GoogleLogin
          onSuccess={handleGoogleLogin}
          onError={handleGoogleError}
          text="signin_with"
          theme="outline"
          size="large"
        />
      </div>
    </GoogleOAuthProvider>
  );
}
