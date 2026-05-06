import { NextRequest, NextResponse } from "next/server";
import { deleteUserCloudData, getUserCloudData, saveUserCloudData } from "@/lib/mongo";

export const runtime = 'nodejs';

const BACKEND_API_URL = process.env.BACKEND_API_URL ?? 'http://localhost:8000';

async function resolveUserId(authHeader: string | null): Promise<string | null> {
  if (!authHeader) return null;
  try {
    const response = await fetch(`${BACKEND_API_URL}/api/profile/`, {
      headers: { Authorization: authHeader },
    });
    if (!response.ok) return null;
    const profile = await response.json();
    return String(profile.id);
  } catch {
    return null;
  }
}

export async function GET(request: NextRequest) {
  if (!process.env.DATABASE_URL) {
    return NextResponse.json(
      { error: 'Cloud sync unavailable: database not configured' },
      { status: 503 }
    );
  }

  const userId = await resolveUserId(request.headers.get('Authorization'));
  if (!userId) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  const userData = await getUserCloudData(userId);
  return NextResponse.json(userData);
}

export async function POST(request: NextRequest) {
  if (!process.env.DATABASE_URL) {
    return NextResponse.json(
      { error: 'Cloud sync unavailable: database not configured' },
      { status: 503 }
    );
  }

  const userId = await resolveUserId(request.headers.get('Authorization'));
  if (!userId) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  const MAX_BODY_SIZE = 1e6;
  const contentLength = request.headers.get("content-length");
  if (contentLength && parseInt(contentLength) > MAX_BODY_SIZE) {
    return NextResponse.json({ error: 'Request body too large' }, { status: 413 });
  }

  const body = await request.json();
  await saveUserCloudData(userId, body.accounts, body.balances);

  return NextResponse.json({ message: 'Cloud data saved successfully' }, { status: 200 });
}

export async function DELETE(request: NextRequest) {
  if (!process.env.DATABASE_URL) {
    return NextResponse.json(
      { error: 'Cloud sync unavailable: database not configured' },
      { status: 503 }
    );
  }

  const userId = await resolveUserId(request.headers.get('Authorization'));
  if (!userId) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  await deleteUserCloudData(userId);
  return NextResponse.json({ message: 'Cloud data deleted successfully' }, { status: 200 });
}
