$(document).ready(function() {
    fetchUserData();
  
    $('#branch, #batch,#role,#tenture').change(function() {
      fetchUserData();
    });
  
    $('#reset-filters').click(function() {
      $('#branch, #batch,#role').val('');
      $('#tenture').val('Last 24 Hours')
      fetchUserData();
    });
  
    // $('#user-data-table').on('click', 'tr', function() {
    //   const email = $(this).find('td:first').text();
    //   fetchUserDetails(email);
    // });
  
    // $('.close').click(function() {
    //   hideUserDetailModal();
    // });
  
    // $(window).click(function(event) {
    //   if (event.target == $('#user-detail-modal')[0]) {
    //     hideUserDetailModal();
    //   }
    // });
  });
  
  function fetchUserData() {
    const branch = $('#branch').val();
    const batch = $('#batch').val();
    const role = $('#role').val();
    const tenture = $('#tenture').val();
    const url = `/get_users?branch=${branch}&batch=${batch}&role=${role}&tenture=${tenture}`;
    $.ajax({
      url: url,
      type: 'GET',
      success: function(data) {
        renderUserDataTable(data);
      },
      error: function(error) {
        console.error('Error fetching user data:', error);
      }
    });
  }
  
  function renderUserDataTable(userData) {
    const tableBody = $('#user-data-table');
    tableBody.empty();
  
    userData.forEach(function(user) {
      const row = $('<tr>');
      row.append($('<td>').text(user.email));
      row.append($('<td>').text(user.role));
      row.append($('<td>').text(user.last_login));
      const statusCell = $('<td>');
      const statusBadge = $('<span>').addClass('user-status').addClass(user.active_status ? 'active' : 'inactive');
      const statusIcon = $('<i>').addClass('bi').addClass(user.active_status ? 'bi-check-circle-fill' : 'bi-x-circle-fill');
      const statusText = $('<span>').text(user.active_status ? 'Active' : 'Inactive');
      statusBadge.append(statusIcon).append(statusText);
      statusCell.append(statusBadge);
      row.append(statusCell);
      tableBody.append(row);
    });
  }
  
  // function fetchUserDetails(email) {
  //   const url = `/get_user_details?email=${email}`;
  
  //   $.ajax({
  //     url: url,
  //     type: 'GET',
  //     success: function(data) {
  //       showUserDetailModal(data);
  //     },
  //     error: function(error) {
  //       console.error('Error fetching user details:', error);
  //     }
  //   });
  // }
//   function showUserDetailModal(userDetails) {
//     const userDetailsDiv = $('#user-details');
//     userDetailsDiv.empty();

//     for (const group of userDetails) {
//         const groupContainer = $('<div>').addClass('group-container');
//         const groupName = $('<h4>').text(group.name);
//         const canvas = $('<canvas>').addClass('pie-chart');

//         groupContainer.append(groupName, canvas);
//         userDetailsDiv.append(groupContainer);

//         const ctx = canvas[0].getContext('2d');
//         renderPieChart(ctx, group);
//     }

//     // Adjust modal layout based on the number of groups
//     const modal = $('#user-detail-modal');
//     modal.addClass('centered-modal');
//     modal.css('display', 'block');
// }

function renderPieChart(ctx, group) {
  const data = [];
  const labels = [];
  const colors = ['#007bff', '#28a745', '#dc3545']; // Colors for different roles

  // Extract data for each role
  for (const [role, messages] of Object.entries(group.messages_by_role)) {
      labels.push(role);
      data.push(messages);
  }

  // Render pie chart
  new Chart(ctx, {
      type: 'pie',
      data: {
          labels: labels,
          datasets: [{
              data: data,
              backgroundColor: colors,
          }]
      },
      options: {
          responsive: false, // Disable responsiveness to fit within the modal
          maintainAspectRatio: false, // Disable aspect ratio for a more compact display
          legend: {
              display: true,
              position: 'bottom' // Display legend at the bottom
          }
      }
  });
}

function hideUserDetailModal() {
  const modal = $('#user-detail-modal');
  modal.css('display', 'none');
}