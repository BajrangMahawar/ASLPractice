// import { Link, useLocation } from 'react-router-dom';
// import {
//   Box,
//   Button,
//   Typography,
//   List,
//   ListItem,
//   ListItemText,
//   ListItemIcon,
// } from '@mui/material';
// import { WordListItem } from '../types/common';
// import CheckCircleIcon from '@mui/icons-material/CheckCircle';
// import CancelIcon from '@mui/icons-material/Cancel';

// const QuizResult: React.FC = () => {
//   const location = useLocation();
//   const { selectedWordList = [] } = location.state || {};

//   return (
//     <Box sx={{
//       maxWidth: "600px",
//       margin: "1.5rem auto",
//       padding: "0 1rem",
//       textAlign: "center",
//       display: "flex",
//       flexDirection: "column",
//       gap: "1rem",
//       position: "relative", }}
//     >
//       <Typography variant="h1" color="primary" sx={{ fontSize: "2rem", fontWeight: 900 }}>Quiz results:</Typography>
//       <List sx={{ width: "70%", margin: "0 auto" }}>
//         {selectedWordList.map((item: WordListItem, index: number) => (
//           <ListItem key={index} sx={{ gap: '0.5rem' }}>
//             <ListItemIcon sx={{ minWidth: 'auto' }}>
//               {item.isCorrect ? (
//                 <CheckCircleIcon sx={{ color: "success.main", fontSize: '2rem' }} />
//               ) : (
//                 <CancelIcon sx={{ color: "error.main", fontSize: '2rem' }} />
//               )}
//             </ListItemIcon>
//             <ListItemText
//               primary={
//                 <Typography sx={{ fontSize: '1.5rem', color: item.isCorrect ? "success.main" : "error.main", textAlign: "center" }}>
//                   <strong>{item.sign}</strong>
//                 </Typography>
//               }
//             />
//           </ListItem>
//         ))}
//       </List>
//       <Box sx={{ display: "flex", flexDirection: "row", gap: "1rem", justifyContent: "center"}}>
//         {/* <Button
//           variant="contained"
//           color="primary"
//           component={Link}
//           to="/wordlist"
//           sx={{ textTransform: "none", width: "25%" }}
//         >
//           Try again
//         </Button> */}
//         <Button
//           variant="contained"
//           color="primary"
//           component={Link}
//           to="/"
//           sx={{ textTransform: "none", width: "25%" }}
//         >
//           Home
//         </Button>
//       </Box>
//     </Box>
//   );
// }

// export default QuizResult;

import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Box,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import { WordListItem } from '../types/common';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

interface ScoreData {
  user_id: number;
  score: number;
  created_at: string;
  quiz_data: WordListItem[];
}

const QuizResult: React.FC = () => {
  const location = useLocation();
  const { selectedWordList = [] } = location.state || {};
  const [scoreData, setScoreData] = useState<ScoreData[]>([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/score/' + localStorage.getItem('userId'))
      .then((response) => {
        if (!response.ok) {
          throw new Error(`API call failed with status: ${response.status}`);
        }
        return response.json();
      })
      .then((data: ScoreData[]) => {
        setScoreData(
          data.map((item) => ({
            ...item,
            quiz_data: JSON.parse(item.quiz_data), // Convert quiz_data string to an array
          }))
        );
        console.log('Fetched score data:', data);
      })
      .catch((error) => {
        console.error('Error fetching score data:', error);
      });
  }, []);

  return (
    <Box
      sx={{
        maxWidth: '600px',
        margin: '1.5rem auto',
        padding: '0 1rem',
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        position: 'relative',
      }}
    >
      <Typography
        variant="h1"
        color="primary"
        sx={{ fontSize: '2rem', fontWeight: 900 }}
      >
        Quiz Results:
      </Typography>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'row',
          gap: '1rem',
          justifyContent: 'center',
        }}
      >
        <Button
          variant="contained"
          color="primary"
          component={Link}
          to="/"
          sx={{ textTransform: 'none', width: '25%' }}
        >
          Home
        </Button>
      </Box>
      {scoreData.map((entry, idx) => (
        <Box
          key={idx}
          sx={{
            marginBottom: '1rem',
            borderBottom: '1px solid #ccc',
            paddingBottom: '1rem',
          }}
        >
          <h4>Score: {entry.score}</h4>
          <Typography>Completed At: {entry.created_at}</Typography>
          <List sx={{ width: '70%', margin: '0 auto' }}>
            {entry.quiz_data.map((item: WordListItem, index: number) => (
              <ListItem key={index} sx={{ gap: '0.5rem' }}>
                <ListItemIcon sx={{ minWidth: 'auto' }}>
                  {item.isCorrect ? (
                    <CheckCircleIcon
                      sx={{ color: 'success.main', fontSize: '2rem' }}
                    />
                  ) : (
                    <CancelIcon
                      sx={{ color: 'error.main', fontSize: '2rem' }}
                    />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography
                      sx={{
                        fontSize: '1.5rem',
                        color: item.isCorrect ? 'success.main' : 'error.main',
                        textAlign: 'center',
                      }}
                    >
                      <strong>{item.sign}</strong>
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      ))}
      {scoreData.length > 0 ? (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'row',
            gap: '1rem',
            justifyContent: 'center',
          }}
        >
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to="/"
            sx={{ textTransform: 'none', width: '25%' }}
          >
            Home
          </Button>
        </Box>
      ) : (
        <></>
      )}
    </Box>
  );
};

export default QuizResult;
