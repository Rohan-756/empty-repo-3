import { type NextRequest, NextResponse } from "next/server"
import { UTApi } from "uploadthing/server"
import { prisma } from '@/lib/prisma'
import { getUserById } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    // Get user from header
    const userId = request.headers.get("x-user-id")
    if (!userId) {
      return NextResponse.json({ error: "User not authenticated" }, { status: 401 })
    }

    const user = await getUserById(userId)
    if (!user || user.role !== "FACULTY") {
      return NextResponse.json({ error: "Access denied - Faculty only" }, { status: 403 })
    }

    // Only handle multipart/form-data
    if (!request.headers.get('content-type')?.includes('multipart/form-data')) {
      return NextResponse.json({ error: 'Invalid content type' }, { status: 400 })
    }
    
    const formData = await request.formData()
    const file = formData.get('resume') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No resume file uploaded' }, { status: 400 })
    }

    // Validate file type (PDF)
    if (file.type !== 'application/pdf') {
      return NextResponse.json({ error: 'Only PDF files are allowed for resumes' }, { status: 400 })
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      return NextResponse.json({ error: 'File size must be less than 5MB' }, { status: 400 })
    }

    // Get faculty record
    const faculty = await prisma.faculty.findUnique({
      where: { user_id: userId },
    })

    if (!faculty) {
      return NextResponse.json({ error: "Faculty profile not found" }, { status: 404 })
    }

    const utapi = new UTApi()

    // Delete old resume if exists
    if (faculty.resume_id) {
      try {
        await utapi.deleteFiles(faculty.resume_id)
        console.log(`Deleted old resume: ${faculty.resume_id}`)
      } catch (error) {
        console.log(`Could not delete old resume file: ${faculty.resume_id}`)
      }
    }

    // Save new resume file to Uploadthing
    const response = await utapi.uploadFiles(file)
    if (response.error) {
      throw new Error(response.error.message)
    }

    const resumeId = response.data.key
    const resumeUrl = response.data.url
    
    // Update faculty record with new resume info
    const updatedFaculty = await prisma.faculty.update({
      where: { id: faculty.id },
      data: {
        resume_id: resumeId,
        resume_path: 'Uploadthing',
      },
    })
    
    return NextResponse.json({ 
      success: true,
      resumeUrl,
      resumeId,
      message: 'Resume uploaded successfully'
    })
  } catch (error) {
    console.error("Resume upload error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest) {
  try {
    // Get user from header
    const userId = request.headers.get("x-user-id")
    if (!userId) {
      return NextResponse.json({ error: "User not authenticated" }, { status: 401 })
    }

    const user = await getUserById(userId)
    if (!user || user.role !== "FACULTY") {
      return NextResponse.json({ error: "Access denied - Faculty only" }, { status: 403 })
    }

    // Get faculty record
    const faculty = await prisma.faculty.findUnique({
      where: { user_id: userId },
    })

    if (!faculty) {
      return NextResponse.json({ error: "Faculty profile not found" }, { status: 404 })
    }

    if (!faculty.resume_id) {
      return NextResponse.json({ error: "No resume found to delete" }, { status: 404 })
    }

    // Delete resume file from Uploadthing
    const utapi = new UTApi()
    try {
      await utapi.deleteFiles(faculty.resume_id)
      console.log(`Deleted resume file: ${faculty.resume_id}`)
    } catch (error) {
      console.log(`Could not delete resume file: ${faculty.resume_id}`)
    }

    // Update faculty record to remove resume info
    await prisma.faculty.update({
      where: { id: faculty.id },
      data: {
        resume_id: null,
        resume_path: null,
      },
    })

    return NextResponse.json({ 
      success: true,
      message: 'Resume deleted successfully'
    })
  } catch (error) {
    console.error("Resume delete error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
} 