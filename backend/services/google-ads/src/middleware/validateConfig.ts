import { Request, Response, NextFunction } from 'express';
import { GoogleAdsConfig } from '../types';
import logger from '../utils/logger';

export const validateConfig = (req: Request, res: Response, next: NextFunction) => {
  const config = req.app.locals.googleAdsConfig as GoogleAdsConfig;

  if (!config) {
    logger.error('Google Ads configuration not found');
    return res.status(500).json({ error: 'Google Ads configuration not found' });
  }

  const requiredFields = [
    'clientId',
    'clientSecret',
    'developerToken',
    'accountId',
    'refreshToken',
  ];

  const missingFields = requiredFields.filter(field => !config[field as keyof GoogleAdsConfig]);

  if (missingFields.length > 0) {
    logger.error('Missing required Google Ads configuration fields', { missingFields });
    return res.status(500).json({
      error: 'Invalid Google Ads configuration',
      missingFields,
    });
  }

  next();
}; 