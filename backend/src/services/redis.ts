import { createClient, RedisClientType } from 'redis';

let redisClient: RedisClientType;

export const initializeRedis = async (): Promise<void> => {
  try {
    redisClient = createClient({
      url: process.env.REDIS_URL || 'redis://localhost:6379'
    });

    redisClient.on('error', (error) => {
      console.error('Redis Client Error:', error);
    });

    redisClient.on('connect', () => {
      console.log('Redis connected');
    });

    redisClient.on('disconnect', () => {
      console.log('Redis disconnected');
    });

    await redisClient.connect();
    
  } catch (error) {
    console.error('Failed to connect to Redis:', error);
    // Redis는 선택적이므로 앱을 종료하지 않음
  }
};

export const getRedisClient = (): RedisClientType => {
  return redisClient;
};

export const setCache = async (key: string, value: any, ttl?: number): Promise<void> => {
  try {
    if (redisClient?.isOpen) {
      const serializedValue = JSON.stringify(value);
      if (ttl) {
        await redisClient.setEx(key, ttl, serializedValue);
      } else {
        await redisClient.set(key, serializedValue);
      }
    }
  } catch (error) {
    console.error('Redis set error:', error);
  }
};

export const getCache = async (key: string): Promise<any> => {
  try {
    if (redisClient?.isOpen) {
      const value = await redisClient.get(key);
      return value ? JSON.parse(value) : null;
    }
    return null;
  } catch (error) {
    console.error('Redis get error:', error);
    return null;
  }
};

export const deleteCache = async (key: string): Promise<void> => {
  try {
    if (redisClient?.isOpen) {
      await redisClient.del(key);
    }
  } catch (error) {
    console.error('Redis delete error:', error);
  }
};

export const clearCachePattern = async (pattern: string): Promise<void> => {
  try {
    if (redisClient?.isOpen) {
      const keys = await redisClient.keys(pattern);
      if (keys.length > 0) {
        await redisClient.del(keys);
      }
    }
  } catch (error) {
    console.error('Redis clear pattern error:', error);
  }
};
