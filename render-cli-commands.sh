#!/bin/bash
# Render CLI Helper Commands for EnableMind Deployment

echo "=== Render CLI Commands for Debugging ==="
echo ""

echo "1. Login to Render:"
echo "   render login"
echo ""

echo "2. List all your services:"
echo "   render services list"
echo ""

echo "3. Get service details:"
echo "   render services get enablemind-research"
echo ""

echo "4. View recent logs:"
echo "   render logs enablemind-research --tail 100"
echo ""

echo "5. Stream live logs:"
echo "   render logs enablemind-research --follow"
echo ""

echo "6. Trigger new deployment:"
echo "   render deploy --service enablemind-research --clear-cache"
echo ""

echo "7. Check deployment status:"
echo "   render deployments list --service enablemind-research"
echo ""

echo "8. Open service in browser:"
echo "   render open enablemind-research"
echo ""

echo "9. SSH into the running container (for debugging):"
echo "   render shell enablemind-research"
echo ""

echo "10. Download/view environment variables:"
echo "    render env list --service enablemind-research"
echo ""

echo "=== Quick Debug Workflow ==="
echo "render login"
echo "render services list  # Find your service name"
echo "render logs enablemind-research --follow  # Watch deployment"
echo "render deploy --service enablemind-research --clear-cache  # Redeploy"
