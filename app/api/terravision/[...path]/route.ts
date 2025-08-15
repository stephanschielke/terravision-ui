import type { Files } from '@/lib/files';
import type { NextRequest } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const basePath = 'http://terravision-api:8001/terravision';
  const path = params.path;
  const searchParams = request.nextUrl.searchParams;

  console.log('=== TERRAVISION GET REQUEST ===');
  console.log('Path:', path);
  console.log('URL:', `${basePath}/${path.join('/')}`);

  const fullUrl = `${basePath}/${path.join('/')}${
    searchParams ? `?${searchParams}` : ''
  }`;

  try {
    const response = await fetch(fullUrl);
    console.log('GET response status:', response.status);

    if (!response.ok) {
      console.error('GET response failed:', response.statusText);
      return new Response('Failed to fetch resource', {
        status: response.status
      });
    }

    // For image responses, preserve content type
    const contentType =
      response.headers.get('content-type') || 'application/octet-stream';
    const responseBody = await response.arrayBuffer();

    return new Response(responseBody, {
      status: response.status,
      headers: {
        'Content-Type': contentType,
        'Content-Length': responseBody.byteLength.toString()
      }
    });
  } catch (error) {
    console.error('GET request failed:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const basePath = 'http://terravision-api:8001/terravision';

  console.log('=== TERRAVISION API ROUTE START ===');
  console.log('Request method:', request.method);
  console.log('Request URL:', request.url);
  console.log('BasePath:', basePath);

  const path = params.path;
  const searchParams = request.nextUrl.searchParams;

  console.log('Path params:', path);
  console.log('Search params:', searchParams?.toString());

  const content: Files = await request.json();
  console.log('Content received, keys:', Object.keys(content));

  // write the editor content to the file system
  const url = `${basePath}/write`;
  console.log('Writing content to backend at:', url);

  try {
    const writeResponse = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(content)
    });

    console.log('Write response status:', writeResponse.status);
    console.log('Write response ok:', writeResponse.ok);

    if (!writeResponse.ok) {
      console.error('Write response failed:', await writeResponse.text());
    } else {
      console.log('Write response success:', await writeResponse.json());
    }
  } catch (error) {
    console.error('Write request failed:', error);
    throw error;
  }

  const fullUrl = `${basePath}/${path.join('/')}${
    searchParams ? `?${searchParams}` : ''
  }`;

  console.log('Fetching from fullUrl:', fullUrl);

  try {
    const response = await fetch(fullUrl);
    console.log('Main response status:', response.status);
    console.log('Main response ok:', response.ok);

    if (!response.ok) {
      console.error('Main response failed:', response.statusText);
    }

    const stream = response.body;
    console.log('=== TERRAVISION API ROUTE END ===');
    return new Response(stream);
  } catch (error) {
    console.error('Main request failed:', error);
    console.log('=== TERRAVISION API ROUTE ERROR END ===');
    throw error;
  }
}
