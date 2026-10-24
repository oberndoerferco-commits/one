import type { APIRoute } from 'astro';
import { askIndexResponse } from '../../lib/ask-index';

export const GET: APIRoute = () => askIndexResponse('it');
