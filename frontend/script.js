
// this is how we hide the time fields based on setting value
document.addEventListener('DOMContentLoaded', e => {
    document.forms.form01.addEventListener('change', e => {
        if (e.target.name == 'setting') {
            let setting = new Boolean(parseInt(e.target.form.setting.value));
            e.target.form.times.disabled = setting.valueOf();
        }
    });
});



const form = document.getElementById('form01');
const result = document.getElementById('result');

async function submitForm(event) {
    e.preventDefault();
    const formData = new FormData(thisForm).entries()
    const response = await fetch('https://localhost:80/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.fromEntries(formData))
    });

    const response_json = await response.json();
    console.log(response_json)
    window.alert("Success!")
    return false
}

form.addEventListener('submit', handleSubmit);

// const thisForm = document.getElementById('form01');
// thisForm.addEventListener('submit', async function (e) {
//     // submitForm(e, this);
//     e.preventDefault();
//     const formData = new FormData(thisForm).entries()
//     const response = await fetch('https://localhost:80/', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(Object.fromEntries(formData))
//     });

//     const result = await response.json();
//     console.log(result)
// });