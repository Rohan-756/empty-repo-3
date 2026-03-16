import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { getUserById } from '@/lib/auth';
import { UTApi } from "uploadthing/server";

// Extract user from x-user-id header
async function getUserFromRequest(req: NextRequest) {
  const userId = req.headers.get('x-user-id');
  if (!userId) return null;
  return await getUserById(userId);
}

// POST: Student applies to an opportunity with resume as form-data
export async function POST(req: NextRequest, { params }: { params: { id: string } }) {
  const user = await getUserFromRequest(req);
  if (!user) return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  if (user.role !== 'STUDENT') return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
  const { id: opportunityId } = params;
  const studentId = user.id;
  try {
    // Check if already applied
    const existing = await prisma.opportunityApplication.findFirst({
      where: { opportunityId, studentId },
    });
    if (existing) return NextResponse.json({ error: 'Already applied' }, { status: 400 });
    // Parse form-data for resume
    const formData = await req.formData();
    const file = formData.get('resume');
    if (!file || typeof file === 'string') {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }
    if (file.type !== 'application/pdf') {
      return NextResponse.json({ error: 'Only PDF files are allowed' }, { status: 400 });
    }
    // Save resume file to Uploadthing
    const utapi = new UTApi();
    const response = await utapi.uploadFiles(file)
    if (response.error) {
      throw new Error(response.error.message)
    }

    const resumeId = response.data.key
    const resumeUrl = response.data.url
    const fileName = file.name

    // Create application with resume ID in DB
    const application = await prisma.opportunityApplication.create({
      data: {
        opportunityId,
        studentId,
        resumePath: resumeId, // Store Uploadthing key here so we know it's in the cloud
        resumeName: fileName, // To display the original filename on frontend
        status: 'PENDING',
      },
    });
    return NextResponse.json(application);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 400 });
  }
} 