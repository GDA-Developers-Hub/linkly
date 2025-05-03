import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import adsRoutes from './routes/ads.routes';
import { GoogleAdsConfig } from './types';
import logger from './utils/logger';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Load Google Ads configuration from environment variables
const googleAdsConfig: GoogleAdsConfig = {
  clientId: process.env.GOOGLE_ADS_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_ADS_CLIENT_SECRET!,
  developerToken: process.env.GOOGLE_ADS_DEVELOPER_TOKEN!,
  accountId: process.env.GOOGLE_ADS_ACCOUNT_ID!,
  refreshToken: process.env.GOOGLE_ADS_REFRESH_TOKEN!,
};

// Store config in app.locals for middleware access
app.locals.googleAdsConfig = googleAdsConfig;

// Routes
app.use('/api/google-ads', adsRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error('Unhandled error', { error: err });
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(port, () => {
  logger.info(`Google Ads service listening on port ${port}`);
}); 