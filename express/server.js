require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');

const app = express();
app.use(cors());

const pool = new Pool({
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  port: process.env.PGPORT,
});

pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('DB connection failed:', err.stack);
  } else {
    console.log('DB connected at:', res.rows[0].now);
  }
});

app.get('/api/:table', async (req, res) => {
  const table = req.params.table;
  if (!['board_details', 'match', 'players'].includes(table)) {
    return res.status(400).json({ error: 'Invalid table name' });
  }

  try {
    const result = await pool.query(`SELECT * FROM ${table} ORDER BY game_datetime LIMIT 100`);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/player/:gameName/:tagLine', async (req, res) => {
  const { gameName, tagLine } = req.params;

  try {
    const result = await pool.query(
      'SELECT * FROM players WHERE game_name = $1 AND tag_line = $2',
      [gameName, tagLine]
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/match_history/:puuid', async (req, res) => {
  
  const { puuid } = req.params;

  try {
    const result = await pool.query(
      'SELECT * FROM match WHERE puuid = $1 LIMIT 10;',
      [puuid]
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err); // Add this
    res.status(500).json({ error: err.message });
  }
});

app.get('/board/:puuid/:match_id', async (req, res) => {
  const { puuid, match_id } = req.params;
  
  try {
    const result = await pool.query(
      'SELECT * FROM board_details WHERE puuid = $1 and match_id = $2;',
      [puuid, match_id]
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err); // Add this
    res.status(500).json({ error: err.message });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});