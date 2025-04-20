// import { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import { Box, Button, TextField, Typography, Link } from "@mui/material";

// const LoginPage: React.FC = () => {
//   const [isSignup, setIsSignup] = useState(false);
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [email, setEmail] = useState("");
//   const navigate = useNavigate();

//   useEffect(() => {
//     // If user is already logged in, redirect to home
//     if (localStorage.getItem("userId")) {
//       navigate("/");
//     }
//   }, [navigate]);

//   const handleSubmit = (event: React.FormEvent) => {
//     event.preventDefault();

//     if (isSignup) {
//       console.log("Signing up with:", { username, email, password });
//     } else {
//       console.log("Logging in with:", { username, password });
//     }

//     // Store userId in localStorage to simulate authentication
//     localStorage.setItem("userId", "12345");
//     navigate("/");
//   };

//   return (
//     <Box
//       sx={{
//         maxWidth: "320px",
//         margin: "2rem auto",
//         padding: "2rem",
//         backgroundColor: "rgba(17, 24, 39, 1)",
//         borderRadius: "0.75rem",
//         color: "rgba(243, 244, 246, 1)",
//         textAlign: "center",
//       }}
//     >
//       <Typography variant="h4" fontWeight={700}>
//         {isSignup ? "Sign Up" : "Login"}
//       </Typography>
//       <form onSubmit={handleSubmit} style={{ marginTop: "1.5rem" }}>
//         {isSignup && (
//           <TextField
//             fullWidth
//             label="Email"
//             variant="outlined"
//             margin="normal"
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//             sx={{ input: { color: "white" }, label: { color: "gray" } }}
//           />
//         )}
//         <TextField
//           fullWidth
//           label="Username"
//           variant="outlined"
//           margin="normal"
//           value={username}
//           onChange={(e) => setUsername(e.target.value)}
//           sx={{ input: { color: "white" }, label: { color: "gray" } }}
//         />
//         <TextField
//           fullWidth
//           label="Password"
//           type="password"
//           variant="outlined"
//           margin="normal"
//           value={password}
//           onChange={(e) => setPassword(e.target.value)}
//           sx={{ input: { color: "white" }, label: { color: "gray" } }}
//         />
//         <Button type="submit" variant="contained" fullWidth sx={{ bgcolor: "rgba(167, 139, 250, 1)", mt: 2 }}>
//           {isSignup ? "Sign Up" : "Sign In"}
//         </Button>
//       </form>
//       <Typography variant="body2" sx={{ marginTop: "1rem", color: "gray" }}>
//         {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
//         <Link href="#" color="inherit" underline="hover" onClick={() => setIsSignup(!isSignup)}>
//           {isSignup ? "Login" : "Sign up"}
//         </Link>
//       </Typography>
//     </Box>
//   );
// };

// export default LoginPage;

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button, TextField, Typography, Link } from '@mui/material';

const LoginPage: React.FC = () => {
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect if user is already logged in
    if (localStorage.getItem('userId')) {
      navigate('/');
    }
  }, [navigate]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    try {
      const endpoint = isSignup
        ? 'http://127.0.0.1:5000/api/signup'
        : 'http://127.0.0.1:5000/api/login';
      const body = isSignup
        ? { username, email, password }
        : { email, password }; // Using email for login

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();
      console.log('data', data);
      if (!response.ok) {
        throw new Error(
          data.error || 'Something went wrong. Please try again.'
        );
      }

      // Store user ID in localStorage
      localStorage.setItem('userId', data.user_id);
      navigate('/');
    } catch (error: any) {
      setError(error.message);
    }
  };

  return (
    <Box
      sx={{
        maxWidth: '320px',
        margin: '2rem auto',
        padding: '2rem',
        backgroundColor: 'rgba(17, 24, 39, 1)',
        borderRadius: '0.75rem',
        color: 'rgba(243, 244, 246, 1)',
        textAlign: 'center',
      }}
    >
      <Typography variant="h4" fontWeight={700}>
        {isSignup ? 'Sign Up' : 'Login'}
      </Typography>

      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}

      <form onSubmit={handleSubmit} style={{ marginTop: '1.5rem' }}>
        <TextField
          fullWidth
          label="Email"
          variant="outlined"
          margin="normal"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          sx={{ input: { color: 'white' }, label: { color: 'gray' } }}
        />
        {isSignup && (
          <TextField
            fullWidth
            label="Username"
            variant="outlined"
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            sx={{ input: { color: 'white' }, label: { color: 'gray' } }}
          />
        )}
        <TextField
          fullWidth
          label="Password"
          type="password"
          variant="outlined"
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          sx={{ input: { color: 'white' }, label: { color: 'gray' } }}
        />
        <Button
          type="submit"
          variant="contained"
          fullWidth
          sx={{ bgcolor: 'rgba(167, 139, 250, 1)', mt: 2 }}
        >
          {isSignup ? 'Sign Up' : 'Sign In'}
        </Button>
      </form>

      <Typography variant="body2" sx={{ marginTop: '1rem', color: 'gray' }}>
        {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
        <Link
          href="#"
          color="inherit"
          underline="hover"
          onClick={() => setIsSignup(!isSignup)}
        >
          {isSignup ? 'Login' : 'Sign up'}
        </Link>
      </Typography>
    </Box>
  );
};

export default LoginPage;
