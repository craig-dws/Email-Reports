"""
Email Reports Automation System - Main Entry Point
Run this script to process monthly reports.
"""

import sys
import argparse
from pathlib import Path
from src.orchestrator import ReportOrchestrator


def main():
    """Main entry point for the Email Reports system."""

    parser = argparse.ArgumentParser(
        description='Email Reports Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run full workflow (extract from Gmail + generate emails + approval tracking)
  python main.py --full

  # Process PDFs already in storage directory
  python main.py --process-pdfs

  # Create drafts for approved emails only
  python main.py --create-drafts

  # Extract PDFs from Gmail only
  python main.py --extract-only
        '''
    )

    parser.add_argument(
        '--full',
        action='store_true',
        help='Run full workflow: extract PDFs, generate emails, create approval tracking'
    )

    parser.add_argument(
        '--extract-only',
        action='store_true',
        help='Extract PDFs from Gmail only (no email generation)'
    )

    parser.add_argument(
        '--process-pdfs',
        action='store_true',
        help='Process PDFs from storage directory (skip Gmail extraction)'
    )

    parser.add_argument(
        '--create-drafts',
        action='store_true',
        help='Create Gmail drafts for approved emails'
    )

    parser.add_argument(
        '--approve-all',
        action='store_true',
        help='Auto-approve all emails without extraction errors (use with caution)'
    )

    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env configuration file (default: .env)'
    )

    args = parser.parse_args()

    # Check if .env file exists
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"ERROR: Configuration file not found: {env_path}")
        print("Please copy .env.example to .env and configure it with your settings.")
        sys.exit(1)

    try:
        # Initialize orchestrator
        orchestrator = ReportOrchestrator(env_file=args.env_file)

        # Execute requested operation
        if args.full:
            print("\n" + "="*60)
            print("RUNNING FULL WORKFLOW")
            print("="*60 + "\n")
            orchestrator.run_full_workflow(
                extract_from_gmail=True,
                create_drafts=False  # Don't auto-create drafts, user must approve first
            )

        elif args.extract_only:
            print("\n" + "="*60)
            print("EXTRACTING PDFs FROM GMAIL")
            print("="*60 + "\n")
            pdf_files = orchestrator.extract_pdfs_from_gmail()
            print(f"\nExtracted {len(pdf_files)} PDF files")

        elif args.process_pdfs:
            print("\n" + "="*60)
            print("PROCESSING PDFs FROM STORAGE")
            print("="*60 + "\n")
            orchestrator.run_full_workflow(
                extract_from_gmail=False,
                create_drafts=False
            )

        elif args.create_drafts:
            print("\n" + "="*60)
            print("CREATING GMAIL DRAFTS FOR APPROVED EMAILS")
            print("="*60 + "\n")
            count = orchestrator.create_drafts_for_approved()
            print(f"\nCreated {count} Gmail drafts")

        elif args.approve_all:
            print("\n" + "="*60)
            print("AUTO-APPROVING ALL EMAILS")
            print("="*60 + "\n")
            orchestrator.approve_all_pending()
            summary = orchestrator.approval_workflow.get_summary()
            print(f"\nApproved: {summary['approved']}")
            print(f"Pending/Needs Revision: {summary['pending'] + summary['needs_revision']}")

        else:
            parser.print_help()
            print("\nERROR: Please specify an operation (--full, --extract-only, etc.)")
            sys.exit(1)

        print("\n" + "="*60)
        print("OPERATION COMPLETE")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        print("\nCheck the log file in logs/ for detailed error information.")
        sys.exit(1)


if __name__ == '__main__':
    main()
